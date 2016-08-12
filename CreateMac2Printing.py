import tkinter
from tkinter import filedialog
import os
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
        htmlfile=open(os.path.join(directory, htmlFilename), "r")
        input=htmlfile.readlines()

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
        header=[]
        navButtons=[[]]
        footerContent=[]
        headerContent=[]
        content=[]

        # First identify the actual content.
        # This begins with '<DIV CLASS="center">' and ends with '</DIV>' and contains an '<A HREF=...</A>'
        startline=-1
        for i in range(0, len(input)-1):
            l=input[i]
            if l.find('<DIV CLASS="center">') > -1:
                startline=i
                break
        if startline == -1:
            print("   ***'<DIV CLASS=\"center\">' not found in "+htmlFilename)
            continue

        endline=-1
        for i in range(startline, len(input)-1):
            l=input[i]
            if l.find("</DIV>") > -1:
                endline=i
                break
        if endline == -1:
            print(" ***'</DIV>' not found in "+htmlFilename)
            continue

        # Transfer the content lines and replace them by a line "@@Content"
        content=input[startline : endline+1]
        del input[startline : endline]
        input[startline]="@@Content"

        # Find and remove any <HR> lines
        for i in range(0, len(input)-1):
            l=input[i]
            if l.find('<HR>') == 0:
                input[i]="@@HR"

        # Find and remove tables of buttons (save the previous and next page nav button information)
        # First identify the actual content.
        # This begins with '<DIV CLASS="center">' and ends with '</DIV>' and contains an '<A HREF=...</A>'
        while True:
            startline=-1
            for i in range(0, len(input)-1):
                l=input[i]
                if l.find('<TABLE ALIGN="center" CLASS="navbar"><TR>') > -1:
                    startline=i
                    break
            if startline == -1:
                break

            endline=-1
            for i in range(startline, len(input)-1):
                l=input[i]
                if l.find("</TR></TABLE>") > -1:
                    endline=i
                    break
            if endline == -1:
                break

            # Confirm that all the intervening lines begin with '<TD CLASS="navbar">'
            if startline+1 > endline-1:
                print(" ***navbar block found without buttons found between " + str(startline)+ " and " + str(endline) + " in " + htmlFilename)
                break
            for i in range(startline+1, endline-1):
                if input[i].find('<TD CLASS="navbar">') != 0:
                    print(" *** line not starting '<TD CLASS=\"navbar\">' found between " + str(startline)+ " and " + str(endline) + " in " + htmlFilename)
                    break
            # Save and then delete the block
            navButtons.append(input[startline : endline])
            del input[startline : endline]
            input[startline]="@@Navbuttons"

        pass
pass