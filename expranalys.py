# -*- utf-8 -*-
##########################################
# PSF license aggrement for expranalys.py
# Developed by Ivan Rybko
# ExprAnalys
##########################################

import re

class ExprAnalys:
    def __init__(self, expr, oplst):
        self.res    = list()
        if len(expr) != 0 and len(oplst) != 0:
            self.expr = expr
            self.oplst  = oplst
        
        # states   = [0,1,2]
        self.curstate = 0

    def check(self, regexp):
        if re.match(re.compile(regexp),self.expr) != None: 
            return True
        else:
            return False

    def getoptoks(self): 
        lst = [(op, self.expr.count(op)) for op in self.oplst if op in self.expr] 
        tmp = ()
        cnt = 0
        while(cnt<len(lst)):
            if cnt > 0 and lst[cnt][1] < lst[cnt-1][1]:
                tmp = lst[cnt]
                lst[cnt] = lst[cnt-1]
                lst[cnt-1] = tmp
            cnt += 1
        self.ops = [tpl[0] for tpl in lst]

    def getop(self, index):
        op = self.ops[index]
        lst = self.expr.split(op)
        self.expr = tuple(lst)
        self.res.append({op: self.expr})

    def gettokens(self):
        if self.curstate == 0:
            op = sefl.ops[0]
            self.expr = tuple(self.expr.split(op))
            self.res.append({ op: self.expr })
            self.curstate = 1

        elif self.curstate == 1:
            cnt = 0
            while(cnt<len(self.ops)):
                op  = self.ops[cnt]
                for elem in self.expr:
                    self.curstate = 0
                    self.gettokens()
                cnt += 1

    def gettoks(self):
        self.getoptoks()
        self.gettokens()
        return self.res

