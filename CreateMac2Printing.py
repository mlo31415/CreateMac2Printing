import tkinter
from tkinter import filedialog
import os
import copy
import Helpers
import operator
import re

# Get the directory containing the directories files to be processed
root = tkinter.Tk()
root.withdraw()
dirname = filedialog.askdirectory()
if len(dirname) == 0:
    exit()

# Get a list of all the filenames of the directories in that directory.
os.chdir(dirname)
dirList = os.listdir(".")
dirList = [f for f in dirList if os.path.isdir(f)]

notNewszines=["Abstract", "Acolyte", "Amor", "AngeliqueTrouvere", "Askew", "Aspidistra", "Austra-Fantasy", "Australian_SFR", "AvramDavidson", "Babel_On", "BEM", "BestOfSusanWood",
             "Bids_etc", "Beyond_Enchanted", "BNF_of_IZ", "Boskone", "BrokenToys", "Censored", "Chanticleer", "Chicon", "Cinvention", "Clevention", "Comic_Art",
             "Confusion", "ConStellation", "Cosmag", "Crifanac", "Cry_of_the_Nameless", "CyberCozen", "Denvention", "Destiny", "Diagonal_Relationship", "Don_Ford_Notebook", "Eastercon",
             "Eclipse", "Enchanted_Duplicator", "Entropy", "Fan-Dango", "Fan-Fare", "FANAC-Updates", "Fanscient", "Fantascience_Digest", "Fantastic_Worlds", "Fantasy_Comics",
              "Fantasy_Comment", "FightingSmofs", "FuturiaFantasia", "Futurian", "GAPAVanguard", "Gardyloo", "Gegenschein", "GenrePlat", "Gotterdammerung",
              "Harlan_Ellison", "Helios", "Hyphen", "IGOTS", "IguanaCon", "Interaction", "Journal_of_SF", "LASFS", "Le_Zombie", "Leaflet", "LeeHoffman", "LeVombiteur", "Loncon",
              "LostToys", "Lunacon", "Mad3Party", "MagiCon", "Mallophagan", "Masque", "MelbourneBulletin", "Mimosa", "Minicon", "Miscellaneous", "Monster", "MT_Void",
              "NebulaAwardsBanquet", "NewFrontiers", "Nolacon", "NOLAzine", "NorWesCon", "NOSFAn", "Novae_Terrae", "NYcon", "ODD", "OKon", "OperationFantast", "Opuntia", "Organlegger",
              "Pacificon", "Peace_on_Sol_III", "Peon", "Phan", "Philcon", "Pittcon", "Planet", "Planeteer", "Plokta", "Polaris", "Pong", "Quandry", "Rhodomagnetic", "Rogers_Cadenhead_APA_Pubs",
              "RUNE", "ScientiComics", "Seacon", "Sense_of_FAPA", "SF", "SF_Advertiser", "SF_Digest", "SF_Digest_2", "SF_Five_Yearly", "SFCon", "SFSFS", "Shangri-LA",
              "Shards_of_Bable", "SkyHook", "Slant", "Solacon", "SpaceDiversions", "SpaceFlight", "SpaceMagazine", "Spaceship", "Spacewarp", "Spaceways", "Speculation",
             "Starlight", "SunSpots", "Syllabus", "TaralWaynePreviews", "TNFF", "TommyWorld", "Tomorrow", "Toto", "Tropicon", "TuckerBag", "Tympany", "Vampire", "Vanations",
             "Vapourware", "Vega", "Vertigo", "VOM", "Wastebasket", "WhatIsSFF", "WildHair", "Willis_Papers", "Wrevenge", "X", "Yandro", "Yokohama", "Zenith"]
notJpegs=["Bullsheet", "Fantasy_Magazine"]

dirList = [f for f in dirList if not f in notNewszines and not f in notJpegs]

# We now have a list of directories to be modified
for directory in dirList:

    print(directory)

    # Create a list of all html files in the directory
    htmlFileList=os.listdir(directory)
    htmlFileList=[f for f in htmlFileList if os.path.splitext(f)[1].lower() == ".html"] # HTML files only
    htmlFileList=[f for f in htmlFileList if os.path.splitext(f)[0][-1:] != "P"] # Don't process printing HTML files which have already been created -- they'll most likely be overwritten.
    sorted(htmlFileList)    # It's easier to follow if it's done in alphabetic order...

    # For each html file in the directory
    for htmlFilename in htmlFileList:

        # Skip index files and those mysterious fox*.html files
        if htmlFilename.find("index") == 0 or htmlFilename.find("fox") == 0:
            continue

        # Skip files ending in "-00" as these are ToC files
        if os.path.splitext(htmlFilename)[0][-3:] == "-00":
            continue

        # Open the file and read it into a list of strings
        with open(os.path.join(directory, htmlFilename), "r") as htmlfile:
            inputHtml=htmlfile.readlines()

        # The structure of the more recent individual page html files is as follows:
        # The name of the file is "<prefix><issue number>-<page number>"
        # The file begins with a pretty standard header.  It should contain the string "/fanzines/zinemix.css"
        # Next is a header line <H1 CLASS=...</H1> -- the content varies from page to page
        # Then a table (the top navigation buttons)
        # After the table, we have a DIV containing the content
        #   We may need to modify the height and width elements of the content
        # Then a horizontal rule (which we'll delete)
        # Then some bottom text which is als content and varies
        # The a bottom table containing another row of navigation buttons (we'll delete this, also)
        # Finally some fixed material

        # But older stuff can be just about anything!

        # It appears that the navigation buttons are always bounded by a table:
        #       <TABLE ALIGN="center" CLASS="navbar"><TR>.....</TR></TABLE>
        # Sometimes there is only one set of navigation buttons

        # It appears that content is always contained in a
        #       <DIV CLASS="center">.....</DIV>
        # It also appears that the image content is always like this:
        #       <A HREF="Fan-Fare33-02.jpeg"><IMG SRC="Fan-Fare33-02.jpeg" HEIGHT="1190" WIDTH="922" BORDER="0"></A>

        # First, find the document HTML header
        # This begins with <!DOCTYPE HTML> and ends with </HEAD></BODY>
        header=Helpers.MarkSection(inputHtml, htmlFilename, '<!DOCTYPE HTML>', "</HEAD><BODY>", False, "@@Header")
        if header == None:
            header=Helpers.MarkSection(inputHtml, htmlFilename, '<!DOCTYPE HTML>', "</HEAD>", True, "@@Header")
            if not Helpers.MarkSection(inputHtml, htmlFilename, '<BODY>', "<BODY>", True, "@@Header"):
                continue

        # And find the HTML footer
        footer=Helpers.MarkSection(inputHtml, htmlFilename, "</BODY></HTML>", None, True, "@@Footer")

        # Next identify the actual content.
        # This begins with '<DIV CLASS="center">' and ends with '</DIV>' and contains an '<A HREF=...</A>'
        content=Helpers.MarkSection(inputHtml, htmlFilename, '<DIV CLASS="center">', "</DIV>", True, "@@Content")
        if content == None:
            continue

        # Find and remove any <HR> lines
        while Helpers.MarkSection(inputHtml, htmlFilename, '<HR>', "", False, "@@HR"):
            pass

        # Find and remove tables of buttons (save the previous and next page nav button information)
        # First identify the actual content.
        # This begins with '<DIV CLASS="center">' and ends with '</DIV>' and contains an '<A HREF=...</A>'
        navButtons=[]
        while True:
            navstuff=Helpers.MarkSection(inputHtml, htmlFilename, '<TABLE ALIGN="center" CLASS="navbar"><TR>', "</TR></TABLE>", False, "@@Navbuttons")
            if navstuff == None:
                break

            # Confirm that all the intervening lines begin with '<TD CLASS="navbar">'
            if len(navstuff) < 2:
                print(" ***navbar block found without buttons found in " + htmlFilename +" in \n"+str(navstuff))
                break
            for i in range(1, len(navstuff)-1):
                if navstuff[i].find('<TD CLASS="navbar">') != 0:
                    print(" *** nav button line not starting '<TD CLASS=\"navbar\">' found in " + htmlFilename)
                    break
            # Save the block
            navButtons.append(navstuff)

        # =======================================================================
        # Now we start building up the printing html page
        # This will be like the original, but with all HRs and all nav buttons removed.
        printingHtml=copy.deepcopy(inputHtml)
        if printingHtml.count("@@HR") > 0:
            printingHtml.remove("@@HR")
        while printingHtml.count("@@Navbuttons") > 0:
            printingHtml.remove("@@Navbuttons")

        # Now locate and drop bottom lines of text.
        # They will be bracketed by <P...</P>
        pattern = re.compile("^<P.*</P>$")  # Regex pattern to match page <P...</P>
        printingHtml=[l for l in printingHtml if not pattern.match(l)]

        # And add the printing line right after the content
        Helpers.InsertLines(printingHtml, "@@Content", ["@@Content", "<P>Printed by Fanac.org at at MidAmericon 2. For <i>much</i> more, see http://fanac.org</P>"], True)

        # Now we need to modify the content lines to include the bounding box
        printingContent = copy.deepcopy(content)

        # Find the '<A REF...</A>' line and surround it with the table code
        aFound=False
        i=0
        while not aFound and i<len(printingContent):
            l=printingContent[i]
            if l.find("<A HREF=") > -1 and l.find("</A>") > -1:
                aFound=True
                printingContent.insert(i, '<table border="1"><tr><td>')
                printingContent.insert(i+2, '</td></tr></table>')
                i=i+2
            i=i+1
        if not aFound:
            print("   ***No '<A HREF...</A>' found in" + str(printingContent))
            continue

        # It is also possible we will need to shrink the jpeg a bit to fit on one page.
        # Scan the content section to find the line containing the IMG spec and parse it
        maxheight=900
        maxwidth=500
        pattern=re.compile("^(.*)HEIGHT=\"([0-9]*)\" WIDTH=\"([0-9]*)\" (.*)$")
        for i in range(0, len(printingContent)-1):
            if pattern.match(printingContent[i]):
                g=pattern.match(printingContent[i]).groups()
                try:
                    height=int(g[1])
                    width=int(g[2])
                except:
                    break
                if height > maxheight or width > maxwidth:
                    scale=min(maxheight/height, maxwidth/width)
                    height=int(scale*height)
                    width=int(scale*width)
                    printingContent[i]=g[0] + 'HEIGHT="' + str(height) + '" WIDTH="' + str(width) + '" ' + g[3]
                break

        # And insert it back into the file.
        if not Helpers.InsertLines(printingHtml, "@@Content", printingContent, True):
            continue

        # Restore the rest of the content
        if not Helpers.InsertLines(printingHtml, "@@Header", header, True):
            continue
        if not Helpers.InsertLines(printingHtml, "@@Footer", footer, True):
            continue

        # Write out the printing version of the page
        splt=os.path.splitext(htmlFilename)
        printFilename=splt[0]+"P"+splt[1]
        printPathname=os.path.join(directory, printFilename)
        #with open(printPathname, "w") as f:
            #f.writelines(printingHtml)

        # =======================================================================
        # OK, now it's time to edit the non-printing html to add the print button
        normalHtml=copy.deepcopy(inputHtml)

        # Get the code for the 1st set of nav buttons
        # This consists of
        #   A <TABLE line
        #   A number of <TD CLASS lines
        #   a </TR></TABLE> line
        if len(navButtons) > 0:
            navstuff=navButtons[0]

            # Step 1 is to remove any previous incarnations of the print button.  We will do this be deleting lines containing the string "Mac2Pframe"
            navstuff=[l for l in navstuff if l.find("Mac2Pframe") == -1]

            # Insert the frame definition just before the nav button block
            navstuff.insert(0, '<iframe src="' + printFilename + '" style="display:none;" name="Mac2Pframe"></iframe>')

            # Insert the new print button between the last two nav buttons
            navstuff.insert(-2, '<TD CLASS="navbar"><form><input type="button" onclick="frames[\'Mac2Pframe\'].print()" value="Print"></form></TD>')

            navButtons[0]=navstuff

        # Now replace all the blocks
        if not Helpers.InsertLines(normalHtml, "@@Content", content, True):
            continue
        if not Helpers.InsertLines(normalHtml, "@@Header", header, True):
            continue
        if not Helpers.InsertLines(normalHtml, "@@Footer", footer, True):
            continue
        if not Helpers.InsertLines(normalHtml, "@@HR", ["<HR>"], False):
            continue
        if len(navButtons) > 0:
            if not Helpers.InsertLines(normalHtml, "@@Navbuttons", navButtons[0], True):
                continue
        if len(navButtons) > 1 and not Helpers.InsertLines(normalHtml, "@@Navbuttons", navButtons[1], True):
            continue

        # Write out the display version of the page
        displayPathname=os.path.join(directory, htmlFilename)
        #with open(displayPathname, "w") as f:
            #f.writelines(normalHtml)


        i=0
        pass
    pass