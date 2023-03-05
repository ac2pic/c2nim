#!/usr/bin/python3
import sys

def isAnnotationLine(line):
    return line.startswith('#-') and line.endswith('-#')

def getAnnotationNameValue(line):
    if not isAnnotationLine(line):
        return ''
    line = line[2:-2].strip()
    name = ""

    idx = 0
    last_char = ""
    for char in line:
        idx += 1
        if char == ":" and last_char != "\\":
            break
        name += char
        last_char = char 

    value = line[idx:].strip()

    return {"name": name, "value": value}

def getAnnotation(lines):
    is_single_line = type(lines) == str
    idx = 0
    line = ''
    if type(lines) == list:
        line = lines[idx]
    elif type(lines) == str:
        line = lines

    if not isAnnotationLine(line):
        return ''

    annoData = getAnnotationNameValue(line)
    if annoData["value"]:
        annoData["lines"] = 1
        return annoData
        
    if not is_single_line:
        annoData["value"] = []
        idx += 1
        while len(lines) > idx:
            line = lines[idx]
            idx += 1
            if isAnnotationLine(line):
                break
            annoData["value"].append(line)
        idx -= 1
    annoData["lines"] = idx + 1
    return annoData

assert getAnnotation("#-abc-#") == {"name": "abc", "value": "", "lines": 1}
assert getAnnotation("#-abc: test-#") == {"name": "abc", "value": "test", "lines": 1}
assert getAnnotation("#-abc-#\na\nb\n#-abc-#\n".split("\n")) == {"name": "abc", "value": ["a", "b"], "lines": 4}

inFile = ''
inputFile = sys.argv[1]
with open(inputFile) as txt:
    inFile = txt.read()

lines = inFile.split("\n")
idx = 0
lines_length = len(lines)
parts = []
while lines_length > idx:
    line = lines[idx]
    if not line.strip():
        idx += 1
        continue
    if not isAnnotationLine(line):
        idx += 1
        continue
    anDict = getAnnotation(lines[idx:])  
    parts.append({"name": anDict["name"], "value": anDict["value"]})
    idx += anDict["lines"]


def generateTestName(name):
    name = name.lower()
    nameParts = name.split(" ")
    nameParts = [namePart.title() for namePart in nameParts]
    return "test_" + ''.join(nameParts)

def generateTest(name, cCode, nimCode):
    testName = generateTestName(name)
    code = '\n'.join([
        "\tdef {}(self):".format(testName),
        "\t\tinputCode = \"{}\"".format(cCode),
        "\t\toutputCode = \"{}\"".format(nimCode),
        "\t\tself.assertStrictEqual(inputCode, outputCode, \"Invalid conversion for {}\")".format(name),
    ])
    return code

baseCode = """
import unittest
from c2nim import C2NimGenerator
from pycparser import c_parser

def toAst(code):
    p = c_parser.CParser()
    return p.parse(code, "<none>")

def toNim(code):
    ast = toAst(code)
    c = C2NimGenerator("<none>")
    return c.visit(ast)

class TestConversion(unittest.TestCase):
""".strip() + "\n"

outFile = baseCode

while len(parts) > 0:
    name = parts[0]["value"]
    inCode = '\n'.join(parts[1]["value"]).encode('unicode_escape').decode('utf-8')
    outCode = '\n'.join(parts[2]["value"]).encode('unicode_escape').decode('utf-8')
    outFile += generateTest(name, inCode, outCode) 
    
    outFile += "\n\n"
    parts = parts[3:]

outputFile = sys.argv[2]

with open(outputFile, 'w') as tests:
    tests.write(outFile)
