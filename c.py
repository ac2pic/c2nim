#!/usr/bin/python3
from pycparser import c_parser

import subprocess
import os
import re
# This is necessary because the parser 
# doesn't like attributes


def parseHeader(headerFilePath):
    result = subprocess.run(["clang", "-isysroot", OO_PATH , "-isystem", OO_INCLUDE_PATH , "-E", headerFilePath],capture_output=True)
    text = result.stdout.decode('utf8')
    text = removeStructAttributes((text))
    # print (text)
    parser = c_parser.CParser()
    ast = parser.parse(text)
    return ast

orbisIncludePath = os.path.join(OO_PATH, "include", "orbis")

orbisHeaderFiles = [
        "/home/ac2pic/PS4Libs/OpenOrbis-PS4-Toolchain/include/orbis/SaveData.h"
]
# for (root, dirs, files) in os.walk(orbisIncludePath, topdown=True):
#     for name in files:
#         if not name.endswith('.h'):
#             continue
#         orbisHeaderFiles.append(os.path.join(root, name))
#     break
# orbisHeaderFiles = [
#     "/home/ac2pic/PS4Libs/OpenOrbis-PS4-Toolchain/include/orbis/Pigletv2VSH.h",
#     "/home/ac2pic/PS4Libs/OpenOrbis-PS4-Toolchain/include/orbis/libmonovm.h",
#     "/home/ac2pic/PS4Libs/OpenOrbis-PS4-Toolchain/include/orbis/Bgft.h",
#     "/home/ac2pic/PS4Libs/OpenOrbis-PS4-Toolchain/include/orbis/Http.h",
#     "/home/ac2pic/PS4Libs/OpenOrbis-PS4-Toolchain/include/orbis/NpCommon.h",
#     "/home/ac2pic/PS4Libs/OpenOrbis-PS4-Toolchain/include/orbis/ImeDialog.h",
#     "/home/ac2pic/PS4Libs/OpenOrbis-PS4-Toolchain/include/orbis/AppInstUtil.h",
#     "/home/ac2pic/PS4Libs/OpenOrbis-PS4-Toolchain/include/orbis/MsgDialog.h",
#     "/home/ac2pic/PS4Libs/OpenOrbis-PS4-Toolchain/include/orbis/CommonDialog.h",
#     "/home/ac2pic/PS4Libs/OpenOrbis-PS4-Toolchain/include/orbis/Net.h",
#     "/home/ac2pic/PS4Libs/OpenOrbis-PS4-Toolchain/include/orbis/Ssl.h",
#     "/home/ac2pic/PS4Libs/OpenOrbis-PS4-Toolchain/include/orbis/Keyboard.h",
#     "/home/ac2pic/PS4Libs/OpenOrbis-PS4-Toolchain/include/orbis/JpegEnc.h",
# ]

asts = []

for orbisHeaderFile in orbisHeaderFiles:
    try:
        asts.append((orbisHeaderFile, parseHeader(orbisHeaderFile)))
    except Exception as e:
        # print("Failed to parse", orbisHeaderFile)
        print(e)

for fp, ast in asts:
    generator = d.C2NimGenerator(fp)
    print(generator.visit(ast))
