# -*- utf-8 -*-
##########################################
# PSF license aggrement for useregexp.py
# Developed by Ivan Rybko
# UseRegExp
##########################################

import re
#
class UseRegExp:
    def __init__(self, kind):
        funcs = edict(**{})
        self.kinds = {
            "digit": self.digits,
            "chars": self.chars,
            "all":   funcs.getunion(self.digits,self.chars),
            }

        self.digits = {
            "all":   "^[0-9]*$",
            "begin": "^[0-9]*",
            "end":   "[0-9]*$",
            "repeat": lambda b,e: "[0-9]{"+"{0},{1}".format(b,e)+"}",
            }

        self.chars = {
            "all":   "^([a-z]|[A-Z])*$",
            "begin": "^([a-z]|[A-Z])*",
            "end":   "([a-z]|[A-Z])*$",
            "repeat": lambda b,e: "([a-z]|[A-Z]){"+"{0},{1}".format(b,e)+"}",
            }

    def count(self, regexp, expr):
        return len(re.findall("({0})".format(regexp), expr))

    def getsubstr(self, regexp, expr):
        return re.split(regexp, expr)

    def subst(self, regexp, substexpr, expr):
        return re.sub(regexp, subst, expr)
