import tkinter
from tkinter import filedialog
import os
import copy
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

toBeSkipped=["Abstract", "Acolyte", "Amor", "AngeliqueTrouvere", "Aspidistra", "AvramDavidson", "BestOfSusanWood", "Bids_etc", "Beyond_Enchanted", "BNF_of_IZ", "Boskone", "Broken Toys",
             "Censored", "Chanticlear", "Chicon", "Cinvention", "Clevention", "Comic_Art", "Confusion", "ConStellation", "Crifanac", "Cry_of_the_Nameless", "Denvention", "Destiny",
             "Diagonal_Relationship", "Don_Ford_Notebook", "Eastercon", "Eclipse", "Enchanted_Duplicxtor", "Entropy", "Fan-Dango", "Fan-Fare", "Fanscient", "Fantascience_Digest",
             "Fantastic_Worlds", "Fantasy_Comics", "Fantasy_Comment", "FightingSmofs", "FuturiaFantasia", "Futurian", "GAPAVanguard", "Gardyloo", "Gegenschein", "GenrePlat"]

dirList = [f for f in dirList if not f in toBeSkipped]

# We now have a list of directories to be modified
for directory in dirList:

    # Create a list of all html files in the directory
    htmlFileList=os.listdir(directory)
    htmlFileList=[f for f in htmlFileList if os.path.splitext(f)[1].lower() == ".html"]

    # For each html file in the directory
    for htmlFilename in htmlFileList:

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

        # We'll go through the contents, modifying as we go
        def MarkSection(input, starttext, endtext, required, replacementtext):
            startline=-1
            for i in range(0, len(input)-1):
                l=input[i]
                if l.find(starttext) > -1:
                    startline=i
                    break
            if startline == -1:
                if required:
                    print("   ***" + starttext + " not found in "+htmlFilename)
                return None

            if endtext != None:
                endline=-1
                for i in range(startline, len(input)-1):
                    l=input[i]
                    if l.find(endtext) > -1:
                        endline=i
                        break
                if endline == -1:
                    if required:
                        print(" ***" + endtext + " not found in "+htmlFilename)
                    return None
            else:
                endline=startline

            # Transfer the content lines and replace them by a line "@@Header"
            savedstuff = input[startline: endline + 1]
            if (endline > startline):
                del input[startline : endline]
            input[startline]=replacementtext
            return savedstuff

        # First, find the document HTML header
        # This begins with <!DOCTYPE HTML> and ends with </HEAD></BODY>
        header=MarkSection(inputHtml, '<!DOCTYPE HTML>', "</HEAD><BODY>", True, "@@Header")
        if header == None:
            continue

        # And find the HTML footer
        footer=MarkSection(inputHtml, "</BODY></HTML>", None, True, "@@Footer")

        # Next identify the actual content.
        # This begins with '<DIV CLASS="center">' and ends with '</DIV>' and contains an '<A HREF=...</A>'
        content=MarkSection(inputHtml, '<DIV CLASS="center">', "</DIV>", True, "@@Content")
        if content == None:
            continue

        # Find and remove any <HR> lines
        while MarkSection(inputHtml, '<HR>', "", False, "@@HR"):
            pass

        # Find and remove tables of buttons (save the previous and next page nav button information)
        # First identify the actual content.
        # This begins with '<DIV CLASS="center">' and ends with '</DIV>' and contains an '<A HREF=...</A>'
        navButtons=[[]]
        while True:
            navstuff=MarkSection(inputHtml, '<TABLE ALIGN="center" CLASS="navbar"><TR>', "</TR></TABLE>", False, "@@Navbuttons")
            if navstuff == None:
                break

            # Confirm that all the intervening lines begin with '<TD CLASS="navbar">'
            if len(navstuff) < 2:
                print(" ***navbar block found without buttons found between " + str(startline)+ " and " + str(endline) + " in " + htmlFilename)
                break
            for i in range(1, len(navstuff)-1):
                if navstuff[i].find('<TD CLASS="navbar">') != 0:
                    print(" *** nav button line not starting '<TD CLASS=\"navbar\">' found in " + htmlFilename)
                    break
            # Save the block
            navButtons.append(navstuff)

        # -----------------------------------------------------------
        # Now we start building up the printing html page
        # This will be like the original, but with ann HRs and all nav buttons removed.
        printingHtml=copy.deepcopy(inputHtml)

        if printingHtml.count("@@HR") > 0:
            printingHtml.remove("@@HR")
        while printingHtml.count("@@Navbuttons") > 0:
            printingHtml.remove("@@Navbuttons")

        # Now we need to modify the content lines to include the bounding box
        printingContent = copy.deepcopy(content)

        # Find the '<A REF...</A>' line and surround it with the table code
        for i in range(0, len(printingContent)):
            pass

    pass