import sys 

INSTR_SET_ONE = {
    "nop":"00",
    "halt":"01",
    "lda":["02", "03"],
    "sta":"04",
    "ldb":["05", "06"],
    "stb":"07",

    "add":["08", "09"],
    "sub":["0a", "0b"],
    "mul":["0c", "0d"],
    "div":["0e", "0f"],
    
    "jp":"10",
    "jpz":"11",
    "outa":"12",
    "outb":"13",
    "out":["14", "15"],

    "mod":["16", "17"]
    
}

INSTR_SET_TWO = {
    "nop":"00",         # no-op
    "halt":"01",        # halt program
    "lda":["02", "03"], # load into A-Register
    "sta":"04",         # store A-Register
    "ldb":["05", "06"], # load into B-Register
    "stb":"07",         # store B-Register
    "add":["08", "09"], # add to A-Register
    "sub":["0a", "0b"], # sub from A-Register
    "outa":"0c",        # display A-Register
    "outb":"0d",        # display B-Register
    "out":["0e", "0f"], # display value
    "jp":"10",          # jump to label
    "jpz":"11",         # jump to label on zero
    "jpc":"12",         # jump to label on carry
    "rts":"13",         # return to subroutine
    "lb":"14",          # loop-back to label
    "lbz":"15",         # loop-back to label on zero
    "lbc":"16",         # loop-back to label on carry
    "rtc":"17",         # return to subroutine on carry
    "rtz":"18",         # return to subroutine on zero
    "lpc":["19", "1a"], # load value into Program-Counter
    "spc":"1b",         # store value of Program-Counter
    "jba":"",           # jump to position by value of A-Register
    "jbb":"",           # jump to position by value of B-Register
}


INSTRUCTIONS = INSTR_SET_TWO

JUMP_POINTS = {}
JUMP_POINTS_AWAIT = {}

def tokenizer(inputString):
    tokens = []

    curPos = 0
    curWord = ""

    while (curPos < len(inputString)):
        curChar = inputString[curPos]

        if (curChar == " " or curChar == "\n" or curChar == "\t"):
            if (len(curWord)>0 and curWord!=" "):
                val = INSTRUCTIONS.get(curWord.lower()) or curWord
                tokens.insert(len(tokens)+1, val)
            curWord = ""
        else:
            curWord = curWord+curChar

        curPos += 1

    return tokens


def grammar2(tokens):
    RESULT = []

    save = False

    curPos = 0
    resPos = 0
    resTok = ""

    while (curPos < len(tokens)):
        curTok = tokens[curPos]
        nextTok = None

        if (curPos+1 < len(tokens)):
            nextTok = tokens[curPos+1]

        if (type(curTok)==list):
            if (nextTok != None):
                if (nextTok[0]=="["):
                    resTok = curTok[1]
                    tokens[curPos+1] = nextTok[1:len(nextTok)-1]

                else:
                    resTok = curTok[0]

                # keep the lines below out of shame, this line 
                # below has cost me 2h of debugging to find as 
                # issue for skipping bytes!!

                # curPos += 1

        else: # adding the token to the result
            # removing formatting to retreive value

            if (curTok[0:2] == "0x"):
                curTok = curTok[2:len(curTok)]
            
            # handling new labels
            if (curTok[0] == ":"):
                JUMP_POINTS[curTok[1:len(curTok)]] = format(resPos, '02x')

                for key in JUMP_POINTS_AWAIT.keys():
                    positions = JUMP_POINTS_AWAIT[key]
                    pointer = JUMP_POINTS.get(key)  # label name
                    
                    if (pointer):
                        # checking for multiple calls for same label
                       
                        if (type(positions) == list):
                            for position in positions:
                                RESULT[position-1] = pointer
                
                curPos += 1
                curTok = ""
                continue

                

                # print(JUMP_POINTS[curTok[1:len(curTok)]])

            foundJump = JUMP_POINTS.get(curTok)

            if (foundJump):
                curTok = foundJump
            else:
                save = True

            

            resTok = curTok

        if (len(resTok)>0):
            RESULT.insert(len(RESULT), resTok)
            resPos += 1

            if (save):
                if (len(resTok)>2):
                    _list = JUMP_POINTS_AWAIT.get(resTok)
                    if (_list):
                        _list.insert(len(_list), resPos)
                    else:
                        JUMP_POINTS_AWAIT[resTok] = [resPos]
                    
                    # print(JUMP_POINTS_AWAIT)
                # print("unknown sub @ ", len(RESULT), " being: ", curTok)
                save = False

            resTok = ""
        
        curPos += 1

    # print(RESULT)
    return RESULT


def loadFile(file_name):
    file = open(file_name, "r")
    res = file.read()
    file.close()
    return res

arguments_num = len(sys.argv)
PRINT_RESULT = False
file_name = None

if (arguments_num == 4):
    file_name = sys.argv[2]
    PRINT_RESULT = True

elif (arguments_num == 3):
    file_name = sys.argv[1]

else:
    print("!! NO FILE PROVIDED !!")
    exit(0)
    
CONTENT = loadFile(file_name)
TOKENS = tokenizer(CONTENT)
GRAMMAR = grammar2(TOKENS)

if (PRINT_RESULT):
    print(" ")
    print("DECODED TOKENS:")
    print(TOKENS)
    print("------------------------------------")
    print("\nAST-Applied: ")
    print(GRAMMAR)
    print("------------------------------------")
    res = ""

    count = 0
    for item in GRAMMAR:
        count += 1
        res+=str(item)+" "
    print("\nRaw-Binary: ")
    print(res)
    print(" ")
    print("Bytes:\n" + str(len(GRAMMAR)) + " / 255\n")
    
    print("#Include <sub-routine>")
    for i in JUMP_POINTS:
        print("\t:"+i)

FORMAT_GRAMMAR = ""
if (INSTRUCTIONS == INSTR_SET_TWO):
    FORMAT_GRAMMAR = "v2.0 raw\n"
FORMAT_WIDTH = 10
COUNTER = 1

for element in GRAMMAR:
    if (COUNTER%FORMAT_WIDTH == 0):
        FORMAT_GRAMMAR = FORMAT_GRAMMAR + GRAMMAR[COUNTER-1] + "\n"
    else:
        FORMAT_GRAMMAR = FORMAT_GRAMMAR + GRAMMAR[COUNTER-1] + " "

    COUNTER += 1


outputFilename = ""
if (len(sys.argv) == 4):
    outputFilename = sys.argv[3]
else:
    outputFilename = sys.argv[2]

outputFile = open(outputFilename+".o", "w")
outputFile.write(FORMAT_GRAMMAR)
outputFile.close()
