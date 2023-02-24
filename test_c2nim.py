#!/usr/bin/python3
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

class TestSum(unittest.TestCase):

    def test_funcdecl(self):
        self.assertEqual(toNim("void a();"),"proc a()\n", "Mismatch in conversion")

    def test_funcpointerdecl(self):
        self.assertEqual(toNim("void (*a)();"),"var a: proc (): void\n", "Mismatch in conversion")

    def test_structdecl(self):
        code = "struct A {};"
        output = "type A {.bycopy.} = object\n"
        self.assertEqual(toNim(code), output,  "Empty struct not converted properly")
