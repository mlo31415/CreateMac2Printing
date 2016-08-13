# We'll go through the contents, modifying as we go
def MarkSection(input, htmlFilename, starttext, endtext, required, replacementtext):
    startline = -1
    for i in range(0, len(input) - 1):
        l = input[i]
        if l.find(starttext) > -1:
            startline = i
            break
    if startline == -1:
        if required:
            print("   ***" + starttext + " not found in " + htmlFilename)
        return None

    if endtext != None:
        endline = -1
        for i in range(startline, len(input) - 1):
            l = input[i]
            if l.find(endtext) > -1:
                endline = i
                break
        if endline == -1:
            if required:
                print(" ***" + endtext + " not found in " + htmlFilename)
            return None
    else:
        endline = startline

    # Transfer the content lines and replace them by a line "@@Header"
    savedstuff = input[startline: endline + 1]
    if (endline > startline):
        del input[startline: endline]
    input[startline] = replacementtext
    return savedstuff


def InsertLines(input, textToBeReplaced, linesToInsert):
    # Scan through input looking for a line containing textToBeReplaced
    for i in range(0, len(input) - 1):
        if input[i] == textToBeReplaced:
            del (input[i])
            input[i:i] = linesToInsert
            return True

    print("   *** Could not find '" + textToBeReplaced + "' in " + str(input))
    return False