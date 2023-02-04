#!/usr/bin/python3
import unittest
from c2nim import C2NimGenerator
from pycparser import c_parser
def toAst(code):
    p = c_parser.CParser() 
    return p.parse(code, "<none>")

class TestSum(unittest.TestCase):
    def test_funcdecl(self):
        input = "void a();"
        expected_output = "proc a()\n"
        c = C2NimGenerator("<none>")
        output = c.visit(toAst(input))
        self.assertEqual(output, expected_output, "Mismatch in conversion")
