#!/usr/bin/python3
from pycparser import c_parser

from c2nim import C2NimGenerator
from export_defines import exportDefines
import sys
import re
import subprocess
import os
def createNimFileName(headerFile):
    headerPath = os.path.normpath(headerFile)
    headerName = headerPath.split(os.sep)[-1]
    headerNameParts = headerName.split('.')
    headerNameParts[-1] = "nim"
    return '.'.join(headerNameParts)

def removeStructAttributes(code):
    new_code = []
    for line in code.split("\n"):
        while "__attribute__" in line:
            line = re.sub("__attribute__((.*))", '', line)
        new_code.append(line)
    return '\n'.join(new_code)

def defToNim(inputFile, outputFile):
    result = subprocess.run(["c2nim", "-o", outputFile, inputFile], capture_output=False)
    print(result.returncode)
    
def parseHeader(headerFilePath):
    OO_PATH = os.environ["OO_PS4_TOOLCHAIN"]
    OO_INCLUDE_PATH = os.path.join(OO_PATH, "include")
    result = subprocess.run(["clang", "", OO_PATH , "-isystem", OO_INCLUDE_PATH , "-E", headerFilePath],capture_output=True)
    text = result.stdout.decode('utf8')
    text = removeStructAttributes(text)
    # print (text)
    parser = c_parser.CParser()
    ast = parser.parse(text)
    return ast
def main():
    header_file = sys.argv[1]
    os.makedirs('./temp', exist_ok=True)
    with open(header_file, 'r') as hf:
        code = hf.read()
    nimFn = createNimFileName(header_file)
    print("Nim file name:", nimFn)
    defines_header_file = './temp/defines_{}.h'.format(nimFn)
    nim_out_file = './temp/{}'.format(nimFn)
    with open(defines_header_file, 'w') as dh:
              dh.write(exportDefines(code))
    with open(nim_out_file, 'w') as nh:
        nh.write('')
    defToNim(defines_header_file, nim_out_file)
    ast = parseHeader(header_file)
    # ast.show()
    g = C2NimGenerator(header_file) 
    print("C Code")
    print(code)
    print("")
    print("Nim code")
    print(g.visit(ast))

if __name__ == "__main__":
    code = sys.argv[1]

    parser = c_parser.CParser()
    ast = parser.parse(code, "<none>")

    g = C2NimGenerator("<none>") 
    print("C Code")
    print(code)
    print("")
    print("Nim code")
    print(g.visit(ast))
    pass
