# -*- utf-8 -*-
########################################
# PSF license aggrement for include.py
# Developed by Ivan Rybko
########################################

import os
import operator
import importlib

def include(argv):
    src = str()
    dst = str()
    if len(argv) < 3:
        print("""Usage: python3.5 include.py moddir=moddir modname=modname """)
    elif len(argv) == 3:
        moddir  = argv[1]
        modname = argv[2]

    src = operator.concat(moddir,"/")
    src = operator.concat(src, modname)
    dst = operator.concat(dst, modname)
    try:
        os.symlink(src, dst)
    except FileExistsError as exc:
        print("change destination name because ",exc)
        exit(-1)
    finally:
        try:
            importlib.import_module(dst)
        except ImportError as exc:
            print(exc)
