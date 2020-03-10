# -*- utf-8 -*-
#####################################
# PSF license aggrement for lexer.py
# Developed by Ivan Rybko
# Lexer
#####################################

class Lexer:
    def __init__(self, expr):
        self.res    = list()
        self.expr   = expr

    def getoptoks(self): 
        optokens = [':=',',','=',' ']
        lst = [(op, self.expr.count(op)) for op in optokens if op in self.expr] 
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
        if len(expr) != 0:
            lst = self.expr.split(op)
            self.expr = tuple(lst)
            self.res.append({op: self.expr})

    def gettokens(self):
        cnt = 0
        while(cnt<len(self.ops)):
            if isinstance(self.expr,tuple):
                tpl = self.expr
                for elem in tpl:
                    self.getop(elem,cnt)
            cnt += 1

    def gettoks(self):
        self.getoptoks()
        self.getop(self.expr, 0)
        self.gettokens()
        return self.res
