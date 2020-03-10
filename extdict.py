# -*- utf-8 -*-
########################################
# PSF license aggrement for extdict.py
# Developed by Ivan Rybko
# ExtDict
########################################

class ExtDict(dict):
    def __init__(self):
        dict.__init__(self)

    def append(self,args):
        if isinstance(args,tuple) and len(args) == 2:
            self.__setitem__(args[0],args[1])
        elif isinstance(args,dict):
            if self.keys() != None:
                for k in args:
                    self[k] = args[k]
            else:
                self = args
    
    def read(self, key=None):
        if key != None and self.__contains__(key):
            return self[key]
        else:
            return list(self.items())
    
    def __setattr__(self, key, value):
        self.append((key,value))

    def __getattr__(self, key):
        return self.read(key)
        
    def tostring(self):
        res = str()
        if self != None:
            for k in self:
                res += k
                res += " = "
                res += str(self[k])
                res += ", "
        return res[:len(res)-2]
    
    def reqdata(self, reqdata):
        if isinstance(reqdata,str):
            for nv in reqdata.split("&"):
                if nv.__contains__("="):
                    self.append(tuple(nv.split("=")))

    def getunion(self, d1=dict, d2=dict): 
        res = dict() 
        for k1 in d1: 
            for k2 in d2: 
                if k1 == k2:
                    res[k1] = [d1[k1],d2[k2]]
        return res 

    def checkdict(self, dct=None):
        if dct == None:
            dct = self

        if isinstance(dct,dict):
            for dk in dct:
                if isinstance(dk,str):
                    if dct.get(dk) == None:
                        print("Error d[{0}".format(dk),"] is None")
                        return False
                    elif dct.get(dk) != None and isinstance(dct[dk], dict):
                        self.checkdict(dct[dk])
                    elif dct.get(dk) != None and not isinstance(dct[dk], dict):
                        return True
                else:
                    return False
        else:
            return False

    def checkkeys(self, defkeys=list):
        data = self
        count = 0
        for item in [data.__contains__(key) for key in list(data.keys())]:
            if item == True:
                count += 1
        if count == len(data):
            return True
        else:
            return False

    def getjson(self, path):
        try:
            with open(path,"rt") as jsonpath:
                self.__dict__ = json.load(jsonpath)
        except FileNotFoundError as err:
            print(err)
            try:
                self.__dict__ = json.loads(path)
            except JSONDecodeError as err:
                print(err)

    def putjson(self, fname = str, data = dict, sortflag=bool, space=int):
        with open(fname,'w+') as fd:
            fd.write(json.dumps(data, sort_keys=sortflag, indent=space))

    def getdata(self, flag=bool):
        if flag == False:
            return self.__dict__
        else:
            return self.__dict__['__dict__']
