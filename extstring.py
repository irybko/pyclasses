# -*- utf-8 -*-
########################################
# PSF license aggrement for extstring.py
# Developed by Ivan Rybko
# ExtString
########################################

import base64

class ExtString(str):
    def __init__(self):
        str.__init__(self)

    def strnstr(self, str1, str2):
        str1 = str1.__add__(str2)
        return str1

    def swap(self, str1, str2):
        step = str()
        step = str1
        str1 = str2
        str2 = step
        return str1,str2

    def tpl2str(self, **kwargs):
        tpl   = kwargs.get("tuple")
        delim = kwargs.get("delim")
        res   = str()
        if delim == None:
            delim = str()
        try:
            for i in tpl:
                if isinstance(i, int) or isinstance(i, float) or isinstance(i,str):
                    res = res.__add__(str(i))
                    res = res.__add__(delim)
                elif isinstance(i, tuple):
                    res = res.__add__(self.tpl2str(**{ "tuple": i, "delim": delim}))
            res = res[:len(res)-1]
            res = res.__add__("\n")
        except AttributeError as exc:
            print(exc)
        finally:
            return res

    def lst2str(self, **kwargs):
        lst   = kwargs.get("list")
        delim = kwargs.get("delim")
        res   = str()
        index = 0
        if delim == None:
            delim = str()
        try:
            lstlen = lst.__len__()
            while(index<lstlen):
                e = lst[index]
                if isinstance(e,str) or isinstance(e, int) or isinstance(e, float):
                    res = res.__add__(str(e))
                elif isinstance(e,bytes):
                    try:
                        res = res.__add__(e.decode("utf-8"))
                    except Exception as exc:
                        print(exc)
                        try:
                            res = res.__add__(base64.decode(e))
                        except Exception as exc:
                            print(exc)
                elif isinstance(e,list):
                    res = res.__add__(self.lst2str(**{ "list": e,"delim": delim }))
                elif isinstance(e,tuple):
                    res = res.__add__(self.tpl2str(**{ "tuple": e,"delim": delim }))
                index+=1
        except (AttributeError, TypeError) as exc:
            print(exc)
        finally:
            return res

    def dct2str(self, **kwargs):
        dct   = kwargs.get("dict")
        kv    = kwargs.get("kv") # tuple True,False or True,True or False,True
        delim = kwargs.get("delim")
        res   = str()
        if delim == None:         delim = str()
        if kv == (True,False):    dctcntnt = list(dct.keys())
        elif kv == (False,True):  dctcntnt = list(dct.values())
        elif kv == (True,True):   dctcntnt = list(dct.items())
        for elem in dctcntnt:
            if isinstance(elem, str) \
                or isinstance(elem, int) \
                or isinstance(elem, float): res = res.__add__(str(elem))
            if isinstance(elem, dict):      res = res.__add__(self.dct2str(**{ "dict": elem, "delim": delim  }))
            if isinstance(elem, list):      res = res.__add__(self.lst2str(**{ "list": elem, "delim": delim  }))
            if isinstance(elem,tuple):      res = res.__add__(self.tpl2str(**{ "tuple": elem,"delim": delim  }))
        return res

    def checktype(self, lst, elemtype):
        count  = 0
        maxlen = len(lst)
        for elem in lst:
            if isinstance(elem, elemtype):
                count += 1
        if count == maxlen:   return True
        else:                 return False

    def concat(self, **kwargs):
        data    = kwargs.get("data")
        delim   = kwargs.get("delim")
        kv      = kwargs.get("kv")        # if elemlist is a dict
        b       = kwargs.get("b")         # if we want to have a bytes representation of the string 
        b64     = kwargs.get("b64")       # if we need to have a base64 representation of thw bytes sequences
        result  = str()

        try:
            if isinstance(data, list):
                if self.checktype(data, str)\
                    or self.checktype(data, int)\
                    or self.checktype(data, float)\
                    or self.checktype(data, bytes)\
                    or self.checktype(data, tuple)\
                    or self.checktype(data, list):      
                    result = self.lst2str(**{ "list": data, "delim": delim })
                elif self.checktype(data, dict):
                    for dct in data:
                        result = result.__add__(self.dct2str(**{ "dict": dct, "delim": delim}))

            elif isinstance(data, dict):     
                result = self.dct2str(**{ "dict": data,"delim": delim, "kv": kv})
            elif isinstance(data, tuple):    
                result = self.tpl2str(**{ "tuple": data,"delim": delim })
            if b == True:
                return bytes(result,"utf-8")
            elif b64 == True:
                return base64.b64encode(bytes(result,"utf-8"))
            elif b   == None or b64 == None:    
                return result
        except TypeError as exc:
            print(exc)                          #unsupported operand type(s) for *: 'NoneType' and 'int'

    def split(self, words):
        lst = list()
        stp = words.split()
        cnt = 0
        for word in stp:
            lst.append(word)
            cnt += 1
            if cnt < len(stp):
                lst.append(" ")
        return lst

    def convert(self, offset):
        res = str()
        lst = self.split(input("type a string: "))
        lstnums = list()
        for word in arr:
            for ch in word:
                lstnums.append(ord(ch))
                for num in lstnums:
                    num += offset
                    res = res.__add__(str(num))
                    res = res.__add__(" ")
        return res

    def deconvert(self, offset, data):
        lst = data.split()
        res = str()
        for num in lst:
            num = int(num)
            num -= offset
            res = res.__add__(chr(num))
            res = res.__add__(" ")
        return res
