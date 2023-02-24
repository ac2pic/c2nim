#!/usr/bin/python3 -i
from typing import TextIO
from pcpp import Preprocessor
import sys
class FakeToken():
    def __init__(self, value):
        self.value = value

class Writer(TextIO):
    def write(self, _):
        pass

class PassThruPreprocessor(Preprocessor):
    def __init__(self, lexer=None):
        super().__init__(lexer)
        self.def_toks = []
    def include(self, a, b):
        return []

    def on_directive_handle(self, directive, toks, ifpassthru, precedingtoks):
        if directive.value == "define":
            # Ignore function defines
            if toks[1].value == "(":
                return
            self.def_toks.append([FakeToken("#")] + [directive] + [FakeToken(" ")] + toks)
            return None
        return None
    def print(self):
        output = ''
        for def_tok in self.def_toks:
            for tok in def_tok:
                output += tok.value
            output += '\n'
        return output

def exportDefines(text):
    p = PassThruPreprocessor()
    p.parse(text)
    p.write(Writer())
    return p.print()
