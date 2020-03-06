# -*- utf-8 -*-
# PSF license aggrement for classeslib.py
# Developed by Ivan Rybko
import os
import sys
import io
import re
import csv
import json
import time
import datetime
import locale
import logging
import importlib
import select
import socket
import codecs
import sqlite3
import pickle
import gzip
import shelve
import itertools
import operator
import math
# binary files io operations
from struct import Struct
import copy
# http
from http import HTTPStatus, client
from http.client import HTTPConnection
from http.server import HTTPServer, \
                        SimpleHTTPRequestHandler, \
                        CGIHTTPRequestHandler, \
                        BaseHTTPRequestHandler
import base64
# mail
import email
from email.mime.text import MIMEText
import email.utils, \
            imaplib, \
            smtplib, \
            smtpd
import uuid
# subprocess
import multiprocessing, \
            subprocess, \
            queue
# wsgi
from wsgiref.simple_server import make_server
from cgi import parse_qs, \
                escape
from urllib.parse import quote
# threading
from threading import Lock
from configparser import ConfigParser
##############################################################################
#   include
##############################################################################
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

##############################################################################
#  Singleton
##############################################################################

class Singleton:
    def __init__(self, aClass):
        self.aClass = aClass
        self.instance = None
    def __call__(self, *args, **kwargs):
        if self.instance == None:
            self.instance = self.aClass(*args, **kwargs)
        return self.instance

##############################################################################
#   edict
##############################################################################

class edict(dict):
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

##############################################################################
#   MyString
##############################################################################

class MyString(str):
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

##############################################################################
#   RegExp
##############################################################################
class RegExp:
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


##############################################################################
# ExprAnalys
##############################################################################

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

#############################################################################
#   Lexer
#############################################################################

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

#############################################################################
#   Searching Algorithms
#############################################################################
class Searching:
    def __init__(self, arr, method):
        self.data = arr
        self.alg  = method

    def linearsearch(self, arr, n, x):
        for i in range (0, n):
            if arr[i] == x:
                return i
            else:
                return -1
                
    def binarySearch(self, l, r, x):
        # Check base case 
        if r >= l:
            mid = l + (r - l)/2
            # If element is present at the middle itself 
            if arr[mid] == x: 
                return mid 
        # If element is smaller than mid, then it  
        # can only be present in left subarray 
            elif arr[mid] > x:
                 return self.binarySearch(arr, l, mid-1, x) 
  
            # Else the element can only be present  
            # in right subarray 
            else: 
                return self.binarySearch(arr, mid + 1, r, x) 
        # Element is not present in the array 
        else:
            return -1
   
    def ternarySearch(self, arr=[], l=int, r=int, x=int):
        if r >= l:
            mid1 = l + (r - l)/3 
            mid2 = mid1 + (r - l)/3
  
            # If x is present at the mid1 
            if arr[mid1] == x:  return mid1
  
            # If x is present at the mid2 
            if arr[mid2] == x:  return mid2

            # If x is present in left one-third
            if arr[mid1] > x: return self.ternarySearch(arr, l, mid1-1, x)
            
            # If x is present in right one-third
            if arr[mid2] < x: return self.ternarySearch(arr, mid2+1, r, x)

            # If x is present in middle one-third
            return self.ternarySearch(arr, mid1+1, mid2-1, x)
        # We reach here when element is not present in array 
        return -1
    
    def jumpSearch(self, arr , x , n ):
        # Finding block size to be jumped 
        step = math.sqrt(n) 
      
        # Finding the block where element is 
        # present (if it is present) 
        prev = 0
        while(arr[int(min(step, n)-1)] < x):
            prev = step
            step += math.sqrt(n)

            if prev >= n:
                return -1
      
        # Doing a linear search for x in  
        # block beginning with prev.
        while(arr[int(prev)] < x):
            prev += 1
          
        # If we reached next block or end  
        # of array, element is not present. 
        if prev == min(step, n): 
            return -1
      
        # If element is found 
        if arr[int(prev)] == x:
            return prev
        else:
            return -1

    def interpolationSearch(self, arr, n, x):
        # Find indexs of two corners 
        lo = 0
        hi = (n - 1) 
   
        # Since array is sorted, an element present 
        # in array must be in range defined by corner 
        while(lo <= hi and x >= arr[lo] and x <= arr[hi]):
            if lo == hi:
                if arr[lo] == x:
                    return lo
                else:
                    return -1; 
          
        # Probing the position with keeping 
        # uniform distribution in mind. 
        pos  = lo + int(((float(hi - lo) / ( arr[hi] - arr[lo])) * ( x - arr[lo]))) 
  
        # Condition of target found 
        if arr[pos] == x: 
            return pos 
   
        # If x is larger, x is in upper part 
        if arr[pos] < x: 
            lo = pos + 1;
        # If x is smaller, x is in lower part 
        else:
            hi = pos - 1
            return -1

    def exponentialSearch(arr, n, x): 
        # Returns the position of first 
        # occurence of x in array 
        # IF x is present at first  
        # location itself
        if arr[0] == x:
            return 0
    
        # Find range for binary search  
        # j by repeated doubling 
        i = 1
        while(i < n and arr[i] <= x):
            i = i * 2
      
        # Call binary search for the found range 
        return self.binarySearch( arr, i / 2, min(i, n), x)

##############################################################################
#   Sorting Algorithms
##############################################################################

class Sorting:
    def __init__(self, method):
        self.method = method

    def cycleSort(self, array):
        writes = 0

        # Loop through the array to find cycles to rotate. 
        for cycleStart in range(0, len(array) - 1): 
            item = array[cycleStart] 
        
            # Find where to put the item. 
            pos = cycleStart
            for i in range(cycleStart + 1, len(array)):
                if array[i] < item:
                    pos += 1
        
            # If the item is already there, this is not a cycle.
            if pos == cycleStart:
                continue
            # Otherwise, put the item there or right after any duplicates. 
            while(item == array[pos]):
                pos += 1
            array[pos], item = item, array[pos] 
            writes += 1
      
            # Rotate the rest of the cycle. 
            while(pos != cycleStart):
                # Find where to put the item. 
                pos = cycleStart 
                for i in range(cycleStart + 1, len(array)): 
                    if array[i] < item:
                        pos += 1
        
            # Put the item there or right after any duplicates. 
            while(item == array[pos]):
                pos += 1
            array[pos], item = item, array[pos] 
            writes += 1
        return writes 
    
    def bubbleSort(self, arr):
        n = len(arr) 
        # Traverse through all array elements 
        for i in range(n):
            # Last i elements are already in place 
            for j in range(0, n-i-1):
                # traverse the array from 0 to n-i-1 
                # Swap if the element found is greater 
                # than the next element 
                if arr[j] > arr[j+1]:
                    arr[j], arr[j+1] = arr[j+1], arr[j]

    def partition(self, arr,low,high):
        # This function takes last element as pivot, places 
        # the pivot element at its correct position in sorted 
        # array, and places all smaller (smaller than pivot) 
        # to left of pivot and all greater elements to right 
        # of pivot
        i = ( low-1 )         # index of smaller element 
        pivot = arr[high]     # pivot 
        
        for j in range(low , high):
            # If current element is smaller than or 
            # equal to pivot 
            if arr[j] <= pivot:
                
                # increment index of smaller element 
                i = i+1 
                arr[i],arr[j] = arr[j],arr[i] 
  
                arr[i+1],arr[high] = arr[high],arr[i+1] 
        return ( i+1 ) 
  
        # The main function that implements QuickSort 
        # arr[] --> Array to be sorted, 
        # low  --> Starting index, 
        # high  --> Ending index 
        # Function to do Quick sort 
    def quickSort(self, arr,low,high): 
        if low < high:
            # pi is partitioning index, arr[p] is now 
            # at right place 
            pi = partition(arr,low,high) 
  
            # Separately sort elements before 
            # partition and after partition 
            quickSort(arr, low, pi-1) 
            quickSort(arr, pi+1, high) 

    def shellSort(self, arr):
        # Start with a big gap, then reduce the gap 
        n = len(arr) 
        gap = n//2
  
        # Do a gapped insertion sort for this gap size. 
        # The first gap elements a[0..gap-1] are already in gapped  
        # order keep adding one more element until the entire array 
        # is gap sorted 
        while(gap > 0):
            for i in range(gap,n):
                
                # add a[i] to the elements that have been gap sorted 
                # save a[i] in temp and make a hole at position i 
                temp = arr[i] 
  
                # shift earlier gap-sorted elements up until the correct 
                # location for a[i] is found 
                j = i 
                while  j >= gap and arr[j-gap] >temp: 
                    arr[j] = arr[j-gap] 
                    j -= gap 
  
                # put temp (the original a[i]) in its correct location 
                arr[j] = temp 
        gap //= 2
  
    # Function to do insertion sort 
    def insertionSort(self, arr):
        # Traverse through 1 to len(arr) 
        for i in range(1, len(arr)):

            key = arr[i]

            # Move elements of arr[0..i-1], that are 
            # greater than key, to one position ahead 
            # of their current position 
            j = i-1
            while j >= 0 and key < arr[j]:
                arr[j + 1] = arr[j] 
                j -= 1
                arr[j + 1] = key 

        # Traverse through all array elements 
        for i in range(len(A)): 
      
            # Find the minimum element in remaining  
            # unsorted array 
            min_idx = i 
       
            for j in range(i+1, len(A)):
                if A[min_idx] > A[j]:
                    min_idx = j 
              
            # Swap the found minimum element with  
            # the first element         
            A[i], A[min_idx] = A[min_idx], A[i] 
            
##############################################################################
#   Logmsg
##############################################################################

@Singleton
class Logmsg:
    def __init__(self, name):
        if isinstance(name, str):
            self.lname = name
            self.lpath = self.lname + ".log"

    def logmsg(self, message):
        # create file handler which logs even debug messages
        logger = logging.getLogger(self.lname)
        logger.setLevel(logging.DEBUG)
        # create file handler which logs even debug info messages
        loghandler = logging.FileHandler(self.lpath)
        loghandler.setLevel(logging.DEBUG)
        # add format
        frmt = logging.Formatter('{asctime} {name} {levelname:8s} {message}',style='{')
        loghandler.setFormatter(frmt)
        logger.addHandler(loghandler)
        # add message
        logger.debug(message)
        logging.info(message)

    def __call__(self, message):
        self.logmsg(message)

def uselog(*args):
    step1 = args[0]
    step2 = args[1]
    log = Logmsg(step1)
    log(step2)

##############################################################################
#   LocalTime
##############################################################################

class LocalTime:
    months_names = [
        ["January","Январь"],
        ["February","Февраль"],
        ["Marth","Март"],
        ["April","Апрель"],
        ["May","Май"],
        ["June","Июнь"],
        ["July","Июль"],
        ["August","Август"],
        ["September","Сентябрь"],
        ["October","Октябрь"],
        ["November","Ноябрь"],
        ["December","Декабрь"]
    ]
    weekdays_names = [
        ["Monday","Понедельник"],
        ["Tuesday","Вторник"],
        ["Wednesday","Среда"],
        ["Thursday","Четверг"],
        ["Friday","Пятница"],
        ["Saturday","Суббота"],
        ["Sunday","Воскресенье"]
    ]
    innerdict = dict()
    innerlist = list()
    lang = int()
    cur_locale = locale.getlocale()
    cur_time = time.localtime()
    def __init__(self):
        self.innerdict = {
           "getyear":            str(self.cur_time.tm_year),
           "getmonthnum":        str(self.cur_time.tm_mon),
           "getmonthname":       str(self.months_names[self.cur_time.tm_mon-1][self.lang]),
           "getmonthday":        str(self.cur_time.tm_mday),
           "getweekday":         str(self.weekdays_names[self.cur_time.tm_wday-1][self.lang]),
           "getyearday":         str(self.cur_time.tm_yday),
           "gethour":            str(self.cur_time.tm_hour),
           "getmin":             str(self.cur_time.tm_min),
           "getsec":             str(self.cur_time.tm_sec),
        }
        self.innerlist = list(self.innerdict.keys())

    def check_locale(self):
        if   ('ru_RU', 'UTF-8') == self.cur_locale: self.lang = 1
        elif ('en_US', 'UTF-8') == self.cur_locale: self.lang = 0
        elif ('en_GB', 'UTF-8') == self.cur_locale: self.lang = 0
        return self.lang

    def getvalue(self, key=str):
        if key in self.innerlist: return self.innerdict[key]

    def addchar(self, func=object):
        step = str()
        if len(str(func())) < 2: step.join([str(0),str(func())])
        else: step.join(str(func()))
        return step

    def __call__(self, delim=str):
        result = str()
        return result.join([
                self.addchar(self.getvalue("getmonthday")), delim,
                self.getvalue("getmonth_name"), delim,
                self.getvalue("getyear"), delim,
                self.addchar(self.getvalue("gethour")), delim,
                self.addchar(self.getvalue("getmin")),  delim,
                self.addchar(self.getvalue("getsec"))
                ])

##############################################################################
#   UseBinaryFile
##############################################################################

class UseBinaryFile:
    def __init__(self):
        self.records = list()
        self.fmt = str()
        self.fd = None

    def write(self, **kwargs):
        """Write a sequence of tuples to a binary file of structures."""
        self.records = kwargs["records"]
        self.fmt     = kwargs["fmt"]
        self.fd      = kwargs["fdescr"]
        record_struct = Struct(self.fmt)

        for record in self.records:
            fd.write(record_struct.pack(*record))

    def read(self, **kwargs):
        """Read a binary file of structures to a sequence of tuples."""
        self.fmt     = kwargs["fmt"]
        self.fd      = kwargs["fdescr"]
        record_struct = Struct(fmt)

        chunks = iter(lambda: self.fd.read(record_struct.size), b'')
        self.records.append((record_struct.unpack(chunk) for chunk in chunks))

##############################################################################
#   UseShelve
##############################################################################

class ShelveWrapper:
    def __init__(self, dbpath=str):
        self.db = shelve.open(dbpath)

    def task(self, **kwargs):
        try:
            record_key  = kwargs.get("primary_key")
            dbpath      = kwargs.get("dbpath")
            action      = kwargs.get("task")
            value       = kwargs.get("value")
        except KeyError as err:
            print(err)
        finally:
            mutex = Lock()
            mutex.acquire()
            if action == "insert":
                with shelve.open(dbpath) as conn:
                    if record_key not in list(conn.keys()):
                        conn[record_key] = value
            elif action == "read":
                with shelve.open(dbpath) as conn:
                    if record_key in list(conn.keys()):
                        return conn[record_key]
            elif action == "update":
                with shelve.open(dbpath) as conn:
                    if record_key in list(conn.keys()):
                        temp = conn[record_key]
                        temp.append(value)
                        conn[record_key] = temp
            elif action == "delete":
                with shelve.open(dbpath) as conn:
                    if record_key in list(conn.keys()):
                        del conn[record_key]
            mutex.release()


##############################################################################
#   Ini
##############################################################################

class Ini:
    "Contains all that is needed to write an INI file"
    def __init__(self, fpath=str):
        "You can add here the begin of your INI file"
        self.content  = dict()
        self.section  = dict()
        self.parser = ConfigParser()
        self.path = fpath

    def addsection(self, section):
        "Add a section delimiter to the INI file"
        self.content[section] = "\n\n[" + section + "]"

    def addkey(self, section, key, value):
        "Writes a string to the INI file"
        self.section[key] = "\n" + key + "=" + value
        try:
            self.content[section] = self.section
        except KeyError:
            self.addsection(section)
            self.content[section] = self.section

    def comment(self, comm):
        "Writes a comment to the INI file"
        self.content["comment"] = "\n ;" + comment

    def write(self):
        step = list()
        with open(self.path, "wt") as fdw:
            for k in self.content:
                step.append("{0} {1}".format(k, self.content[k]))
            fdw.writelines(step)

    def read(self):
        self.parser.read(self.path, encoding='utf-8')
        sections = self.parser.sections()
        for section_name in sections:
            items = self.parser.items(section_name)
            self.content[section_name] = items

    def showdata(self):
        for k in self.content:
            print(k, self.content[k])

    def getdata(self):
        return self.content

##############################################################################
#   ExecuteApp
##############################################################################

class ExecuteApp:
    def __init__(self, **kwargs):
        self.__dict__ = kwargs

    def worker(self, values):
        try:
            popenargs = self.__dict__["args"], self.__dict__["env"],\
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            proc = subprocess.Popen(popenargs)
        except (OSError, ValueError) as exc:
            print(exc)
        finally:
            if isinstance(values, tuple) or isinstance(values, list):
                for v in values:
                    proc.stdin.write(bytes(v,"utf-8"))
            elif isinstance(values, dict):
                for v in values:
                    proc.stdin.write(bytes(values[v],"utf-8"))
            elif isinstance(values, queue.Queue):
                while(values.empty() != True):
                    proc.stdin.write(bytes(values.get(),"utf-8"))

            proc.stdin.close()
            self.pid = proc.pid
            step = proc.stdout.read().decode("utf-8")
            proc.stdout.close()
            self.end()
            return step

    def runwsgi(self):
        """ Usage: ExecuteApp().runwsgi()"""
        srvr = make_server(self.__dict__["env"]["host"], self.__dict__["env"]["port"], self.runapp)
        srvr.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
        srvr.serve_forever()

    def runapp(self, environ, start_response):
        return self.__dict__.get("wsgiapp")(self.__dict__.get("env"), start_response)()

    def end(self):
        try:
            os.kill(self.pid, signal.SIGTERM)
        except OSError as exc:
            print(exc)

    def imode(self):
        keyword = self.__dict__["keyword"]
        actions = self.__dict__["actions"]
        print("""If you want to exit type {0} \n
        If you want to call an action:\n
            1) without args type key only;\n 
            2) with args type key = args where args is a sequence via comma; \n
        Avialable keys are : {1} of current actions""".format(keyword, list(actions.keys()))) 
        while(f):
            expr = str(input("$> "))
            delim = "="
            index = int()
            try:
                index = e.index(delim)
            except ValueError as exc:
                func = actions.get(expr)
                if func != None:
                    func()
            finally:
                lst1 = e.split(delim)
                if len(lst1) >=2:
                    func = actions.get(lst1[0])
                    if func != None:
                        args = tuple()
                        cnt = 0
                        lst2 = lst1[1].split(",")
                        for i in lst2:
                            args += (i,)
                        func(args)
            if e == keyword:
                f = False

##############################################################################
# EncoderDecoder
##############################################################################

class EncDec:
    def __init__(self):
        self.offset = ord(time.tzname[0][0])
        self.data = dict()

    def encoder(self):
        seq = str(input("type sentence: "))
        cnt = 0
        res = str()
        while(cnt < len(seq)):
            res += chr(ord(seq[cnt])*self.offset)
            cnt += 1
            self.data[seq] = res
    def decoder(self):
        seq = str(input("type sentence: "))
        cnt = 0
        res = str()
        while(cnt < len(seq)):
            res += chr(ord(seq[cnt])//self.offset)
            cnt += 1
            self.data[seq] = res
    def getdata(self):
        return self.data


##############################################################################
#   MultiplexIO
##############################################################################

class MultiPlexIO:
    incoming_messages = multiprocessing.Queue()
    outgoing_messages = multiprocessing.Queue()
    exceptions        = multiprocessing.Queue()

    flag = { "inc": True, "out": True, "exc": True }

    def __init__(self, **kwargs):
        self.host   = kwargs.get("host")
        self.port   = kwargs.get("port")
        self.qsize  = kwargs.get("backlog")
        if self.qsize:
            self.role   = "server"
        else:
            self.role   = "client"

        self.proto  = kwargs.get("proto")
        self.nbytes = kwargs.get("bytes")

    def serve_forever(self, consumer_target, *target_parameters):
        evproducer = multiprocessing.Process(target=self.evloop)
        evproducer.daemon=True
        consumer = multiprocessing.Process(target=consumer_target,args=(target_parameters))
        consumer.daemon=True
        producer.start()
        consumer.start()
        producer.join(1)
        comsumer.join(1)

    def createsocket(self, port_offset):
        if self.proto == "tcp":
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        elif self.proto == "udp":
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        if self.role == "client":
            sock.connect((self.host,self.port))
        elif self.role == "server":
            sock.setblocking(True)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
            sock.bind((self.host,self.port+port_offset))
            sock.listen(self.qsize)
        return sock

    def evloop(self):
        flag = True
        try:
            rlist = self.createsocket()
            wlist = self.createsocket()
            elist = self.createsocket()
            while flag:
                readable,writeable,exceptable = select.select([rlist],[wlist],[elist])
                self.recvdata(readable)
                self.senddata(writeable)
                self.getexceptions(exceptable)
        except KeyboardInterrupt:
            flag = False

    def recvdata(self, readable):
        if self.role == "server":
            for each in readable:
                #data = each.accept()[0].recv(self.nbytes).decode("utf-8").split("\n")
                data = each.accept()[0].recv(self.nbytes).decode("utf-8")
                print(data)
                self.incoming_messages.put_nowait(data)

        if self.role == "client":
            for each in readable:
                data = each.recv(self.nbytes).decode("utf-8").split("\n") # makes a list
                print(data)
                self.incoming_messages.put_nowait(data)

    def senddata(self, writeable):
        if self.role in ["client","server"]:
            for each in writeable:
                if self.flag["out"] == False:
                    data = self.outgoing_messages.get()
                    print(data)
                    each.send(bytes(data,"utf-8"))

    def getexceptions(self, exc):
        for each in exc:
            self.exceptions.put_nowait(each)

    def read_exceptions(self):
        while(self.exceptions.empty() != True):
            print(self.exceptions.get())

##############################################################################
#   HTTPNode not tested
##############################################################################

class HTTPNode(MultiPlexIO):
    # server side
    ssqueuetosend = queue.Queue()
    ssqueuetorecv = queue.Queue()

    # client side
    csqueuetosend = queue.Queue()
    csqueuetorecv = queue.Queue()

    request_headers = list()
    response_headers = list()

    def __init__(self, **kwargs):

        kwargs["proto"] = "http"
        kwargs["bytes"] = 65536

        MultiPlexIO.__init__(self, **kwargs)

    def parseqs(self, reqstring, delim):
        step = dict()
        if delim == None: data = reqstring.split("&")
        else:             data = reqstring.split(delim)[1].split("&")
        if len(data) == 1: return None
        else:
            for pair in data:
                step[pair.split("=")[0]] = pair.split("=")[1]
            return step

    def parseheaders(self, sequence, lbound, hbound):
        idx = 0
        headers = list()
        for item in sequence:
            if idx >= lbound and idx <= hbound:
                headers.append(item)
                idx += 1
        return headers

    def read_incomings(self):
        if self.role == "server":
            lst = self.incoming_messages.get() # data = list
            count = 0
            for each in lst:
                if count == 0 and re.match(re.compile("^POST"), lst[count].split(" ")[0]) != None:
                    lastindex = len(lst) - 1
                    msg = {
                        "headers": lambda: self.parseheaders(lst, 1, lastindex),
                        "body":    lambda: self.parseqs(lst[lastindex])
                    }
                    self.received_postrequests.put(msg)

                elif count == 0 and re.match(re.compile("^GET"), lst[count].split(" ")[0]) != None:
                    lastindex = len(lst) - 1
                    msg = {
                        "headers": lambda: self.parseheaders(lst, 1, lastindex),
                        "body":    lambda: self.parseqs(lst[lastindex], "?")
                    }
                    self.received_getrequests.put(msg)

        elif self.role == "client":
            while(self.incoming_messages.empty() == False):
                data = self.incoming_messages.get()
                self.csqueuetorecv.put_nowait(data)

    def reqheader(self, hkey, hvalue):
        self.request_headers.append("{hkey}: {hvalues}".format(hkey,hvalues))
    def respheader(self, hkey, hvalue):
        self.response_headers.append("{hkey}: {hvalues}".format(hkey,hvalues))

    def reqdata(self, **kwargs):
        if self.role == "client":
            self.csqueuetosend.put_nowait({ "headers": self.request_headers,"body": kwargs })

    def respdata(self, **kwargs):
        if self.role == "server":
            self.ssqueuetosend.put_nowait({ "headers": self.response_headers,"body": kwargs })

    def write_outgoings(self):
        if self.role == "server":
            while(self.ssqueuetosend.empty() == False \
            and self.ssqueuetosend.full() == False):
                self.outgoing_messages.put(self.ssqueuetosend.get())

        if self.role == "client":
            while(self.csqueuetosend.empty() == False \
            and self.csqueuetosend.full() == False):
                self.outgoing_messages.put(self.csqueuetosend.get())

##############################################################################
#   HTTPServerNode not tested
##############################################################################

class HTTPServerNode(HTTPNode):
    def __init__(self, **kwargs):
        kwargs["role"] = "server"
        HTTPNode.__init__(self, **kwargs)

##############################################################################
#   HTTPClientNode not tested
##############################################################################

class HTTPClientNode(HTTPNode):
    def __init__(self, **kwargs):
        kwargs["role"] = "client"
        HTTPNode.__init__(self, **kwargs)

##############################################################################
#    Request and Response classes and functions
##############################################################################

@Singleton
class CORSSettings:
    def __init__(self):
        self.__dict__ = {
             'html': ("Content-Type","text/html charset=UTF-8"),
              'css': ("Content-Type","text/css charset=UTF-8"),
               'js': ("Content-Type","text/javascript charset=UTF-8"),
             'json': ("Content-Type","application/json charset=UTF-8"),
              'txt': ("Content-Type","text/plain charset=UTF-8"),
              'xml': ("Content-Type","text/xml charset=UTF-8"),
              'csv': ("Content-Type","text/csv charset=UTF-8"),
              'rtf': ("Content-Type","text/rtf charset=UTF-8"),
              'uri': ("Content-Type","text/uri-list charset=UTF-8"),
              'bmp': ("Content-Type","image/bmp"),
              'gif': ("Content-Type","image/gif"),
             'jpeg': ("Content-Type","image/jpeg"),
              'jpg': ("Content-Type","image/jpg"),
              'png': ("Content-Type","image/png"),
              'svg': ("Content-Type","image/svg+xml"),
       'font_types': [("Content-Type","image/tiff"),("Content-Type","image/tiff-fx")]
        }
        self.corsheaders = [
            ("Access-Control-Allow-Origin","*"),
            ("Access-Control-Allow-Credentials","true"),
            ("Access-Control-Allow-Methods","GET, POST, PUT, DELETE, OPTIONS"),
            ("Access-Control-Allow-Headers","Accept,Authorization, Cache-Control,Content-Type, DNT, If-Modified-Since, Keep-Alive, Origin, User-Agent, X-Requested-With"),
            # Tell client that this pre-flight info is valid for 20 days
            ("Access-Control-Max-Age","1728000") ]

    def __getitem__(self, key):
        assert key in list(self.__dict__.keys()), "content-type disallows"
        return self.__dict__[key][0],self.__dict__[key][1]

    def getheaders(self):
        return self.corsheaders

    def getmsgbycode(self, code=int):
        subst_map = {
            "value": HTTPStatus(code).value,
            "phrase": HTTPStatus(code).phrase,
            "description": HTTPStatus(code).description
        }
        resp = "HTTP/1.1 {value} {phrase} {description}".format_map(subst_map)
        return resp

cors = CORSSettings()

logs = {
    "static":     Logmsg("staticserver"),
    "dynamic":    Logmsg("dynamicserver"),
    "httpserver": Logmsg("httpserver"),
    "smtpserver": Logmsg("smtpserver"),
    "wsgiserver": Logmsg("wsgiserver"),
    "wsgiapp":    Logmsg("wsgiapp"),
    "imapclient": Logmsg("imapclient"),
    "smtpclient": Logmsg("smtpclient"),
    "httpclient": Logmsg("httpclient"),
    "dbrequest":  Logmsg("dbrequest") 
    }

env = dict()
email_message = str()
mystr = MyString()

def concat(s1,s2):
    res = str()
    res = res.__add__(s1)
    res = res.__add__(s2)
    return res

requestmessages = queue.Queue()
responsemessages = queue.Queue()

httpkeys = ["rpath","host","port","kind"]
dbkeys   = httpkeys + ["dbpath","sqltemplatespath"]
httpconf = dict().fromkeys(httpkeys)
dbconf   = dict().fromkeys(dbkeys)
extdct   = edict()
"""
    querytemplates - the dictionary with keys that opens prepared statements templates from
    external json-file with records like:
    {
          "createdb": "create table {0}({1},{2},{3},...);",
            "dropdb": "drop table {0};",
        "insertinto": "insert into {0}({colnames_list}) values({0},{1},{2},...);",
         "selectall": "select {1},{2},... from {0};",
            "update": "update {0} set {1} = {2}, ...;",
         "deleteall": "delete from {0};"
    }
    where {0} means relation name, {1},{2},{3},... means attribute names or current values
    for example:
        1) crt = "create table {0}({1},{2},{3})"
        2) crt.format("cars","id integer primary key","name text unique","price float")
           "create table cars(id integer primary key,name text unique,price float)"
"""
querytemplates = dict()

def makepreformatexpr(string):
    res = re.findall("{\w+\}",string)
    if res != None:
        dct = dict()
        values = str()
        cnt = 0
        for each in res:
            each = each[1:len(each)-1]
            dct[each] = "{%s}" % cnt
            cnt += 1
            try:
                return string.format_map(dct)
            except KeyError as exc:
                print(exc)

def getconfig(path):
    extdct = edict()
    extdct.getjson(path)
    return extdct.getdata(True)

def setconfig(lstargs):
    maxlen = len(lstargs)
    if maxlen < 3:
        print("""\
            Usage: {0} [options] [arguments] \
                -p  parameters in command line in format name=value&name=value&... 
                    parameters be equal {1} or {1} and {2} in same time.
                    {1} allow to run http server 
                    {2} allow to run http and db servers
                -f  parameters enclosed in json file format.
                    keys are the same of {1} or {1} and {2}
            """.format(__file__, httpkeys, dbkeys))
    elif lstargs[1] == "-p":
        dct = edict()
        for elem in lstargs[2].split("&"):
            dct.append(tuple(elem.split("=")))
        if dct.checkkeys(httpkeys):
            httpconf = dct
        elif dct.checkkeys(dbkeys):
            dbcong = dct
    elif lstargs[1] == "-f":
        dct = getconfig(lstargs[2])
        if dct.checkkeys(httpkeys) and tuple(dct.values()) != (None,None,None,None):
            httpconf = dct
        elif dct.checkkeys(dbkeys) and tuple(dct.values()) != (None,None,None,None,None,None):
            httpconf["rpath"] = dct["rpath"]
            httpconf["host"]  = dct["host"]
            httpconf["port"]  = dct["port"]
            httpconf["kind"]  = dct["kind"]
            #
            dbconf["dbpath"]  = dct["dbpath"]
            dbconf["sqltemplatespath"] = dct["sqltemplatespath"]
            querytemplates    = getconfig(dbconf["sqltemplatespath"])

class TextMessage:
    """
        Create a message for an email.
        from:         Email address of the sender.
        to:           Email address of the receiver.
        subject:      The subject of the email message.
        message_text: The text of the email message.
    """
    def __init__(self, **kwargs):
        self.keys  = ["sender","receiver","subject","message","addition"]
        self.outer = ReqRes
        if kwargs != None and list(kwargs.keys()) == self.keys:
            for k in kwargs:
                self.__setattr__(k, kwargs.get(k))

    def __repr__(self, msg):
        return base64.urlsafe_b64encode(self.__dict__.as_string())

    def __setattr__(self, attr, value):
        assert attr in self.keys, " not allowed"
        if attr == "sender":      self.__dict__["From"]     = value
        elif attr == "receiver":  self.__dict__["To"]       = value
        elif attr == "subject":   self.__dict__["Subject"]  = value
        elif attr == "message":   self.__dict__["Message"]  = smtplib.MIMEText(value)
        elif attr == "addition":
            if isinstance(value,dict):
                kwargs = {
                    "rootpath": value.get("rootpath"),
                    "avctypes": value.get("avctypes")
                    }
                self.__dict__["resources"] = getstaticresources(**kwargs)

    def __getattr__(self, attr):
        assert attr in self.keys, " not allowed"
        if attr == "sender":     return self.__dict__["From"]
        elif attr == "receiver": return self.__dict__["To"]
        elif attr == "subject":  return self.__dict__["Subject"]
        elif attr == "message":  return self.__dict__["Message"]
        elif attr == "addition": return self.__dict__["resources"]

class IMAPClient:
    def __init__(self, **kwargs):
        self.servername = kwargs.get("host")
        self.serverport = kwargs.get("port")
        self.ssl        = kwargs.get("ssl")
        self.username   = kwargs.get("username")
        self.password   = kwargs.get("password")
        self.address    = kwargs.get("address")

        logs["imapclient"](repr(self))

        try:
            if self.ssl: self.conn = imaplib.IMAP4_SSL(self.servername)
            else:        self.conn = imaplib.IMAP4(self.servername)
        except Exception as exc:
            print(exc)
        finally:
            self.conn.login(self.username, self.password)
            self.imapqueue = queue.Queue()

    def __del__(self):
        self.conn.close()
        self.conn.logout()

    def imapsumm(self):
        self.conn.select('Inbox')
        step = self.conn.search(None, 'ALL')
        step = step[1]
        return sum(num for num in step[0].split())

    def imapgetone(self, num):
        self.conn.select('Inbox')
        status, data = self.conn.fetch(str(num), "(RFC822)")
        self.email_message = email.message_from_string(data[0][1])
        self.imapqueue["req"] = self.email_message

    def imapremoveone(self, num):
        self.conn.select("Inbox")
        self.conn.store(num, '+FLAGS', r'\Deleted')
        self.conn.expunge()

    def imapremoveall(self):
        maxlen = self.imapsumm()
        num = 0
        while(num<=maxlen):
            self.imapremoveone(num)
            num += 1

    def imapgetlatestemailsentto(self):
        timeout=300
        poll=1
        start_time = time.time()
        while ((time.time() - start_time) < timeout):
            status, data = self.conn.select('Inbox')
            if status != 'OK':
                time.sleep(poll)
            continue
            status, data = self.conn.search(None, 'TO', self.address)
            data = [d for d in data if d is not None]
            if status == 'OK' and data:
                for num in reversed(data[0].split()):
                    status, data = self.conn.fetch(num, '(RFC822)')
                    email_msg = email.message_from_string(data[0][1])
                    self.imapqueue["req"] = email_msg
            time.sleep(poll)
            raise AssertionError("No email sent to {0} found in inbox after polling for {1} seconds.".format(email_address, timeout))

    def imapremovemsgssentto(self):
        self.conn.select('Inbox')
        status, data = self.conn.search(None, 'TO', self.address)
        if status == 'OK':
            for num in reversed(data[0].split()):
                status, data = self.conn.fetch(num, '(RFC822)')
                self.conn.store(num, '+FLAGS', r'\Deleted')
                self.conn.expunge()

class Request:
    def httprequest(**kwargs):
        host    = kwargs.get("host")
        port    = kwargs.get("port")
        reqtype = kwargs.get("reqtype")
        headers = kwargs.get("headers")
        url     = kwargs.get("url")

        logs["httpclient"]((host, port, reqtype, headers, url))

        response = dict().fromkeys(["status","headers","reason","body"])

        if reqtype == "get":
            try:
                conn = HTTPConnection(host,port)
                conn.request("GET", url, headers)
            except Exception as exc:
                print(exc)
            finally:
                rdata = conn.getresponse()
                rheaders = rdata.getheaders()
                rbody = str()
                step = [elem for elem in rheaders if "Content-Length" in elem]
                datasz = int(step[0][1])
                rbody  = rdata.read(datasz).decode("utf-8")

                logs["httpclient"]("== get method data==")
                logs["httpclient"]((rdata, rheaders, rbody))

                response["status"]   = rdata.status
                response["headers"]  = rheaders
                response["reason"]   = rdata.reason
                response["body"]     = rbody

                conn.close()
                return response

        elif reqtype == "post":
            body = kwargs.get("body")
            try:
                conn = HTTPConnection(host,port)
                conn.request("POST", url, body, headers)
            except Exception as exc:
                print(exc)
            finally:
                rdata = conn.getresponse()
                respheaders = rdata.getheaders()

            return { 
                "status":  rdata.status,
                "headers": respheaders,
                "reason":  rdata.reason 
                }
            conn.close()

            logs["httpclient"]("== post method data ==")
            logs["httpclient"]((rdata, respheaders, respbody))


    def smtprequest(**kwargs):
        host  = kwargs.get("host")
        port  = kwargs.get("port")
        message = kwargs.get("message")


        logs["smtpclient"]("== smtp request data==")
        logs["smtpclient"]((rdata, respheaders, respbody))

        if isinstance(message, TextMessage):
            if message.sender != None and message.receiver != None and message.subject  != None and message.message  != None:
                smtpclient = smtplib.SMTP((host,port))
                smtpclient.set_debuglevel(True)  # show communication with the server
                try:
                    smtpclient.sendmail(message.sender,message.receiver,message.subject,message.message)
                except SMTPException as exc:
                    print(exc)
                finally:
                    smtpclient.quit()

    def imaprequest(**kwargs):
        action = kwargs.get("action")
        number = kwargs.get("number")

        logs["imapclient"]("== smtp request data==")
        logs["imapclient"]((rdata, respheaders, respbody))

        imapclient = IMAPClient(**kwargs)

        if action == "imapsumm":                        return imapclient.imapsumm()
        elif action == "imaprmvone" and instance(number,int):  imapclient.imapremoveone(number)
        elif action == "imaprmvall":                           imapclient.imapremoveall()
        elif action == "imapgetone":                    return imapclient.imapgetone(number)
        elif action == "imapgetlatestemailsentto":             imapclient.imapremovemsgssentto()
        elif action == "imapremovemsgssentto":                 imapclient.imapremovemsgssentto()

###################################################################################################################
#  Common functions for several servers
###################################################################################################################

def getdata(rpath, reqheaders):
    result  = dict()
    result["statusline"] = tuple()
    result["headers"]    = list()
    result["data"]       = list()
    F = bool()

    if os.path.exists(rpath):
        result["statusline"] = (200, cors.getmsgbycode(200).encode("utf-8"))
        for elem in cors.getheaders():
            result["headers"].append(elem)
        result["headers"].append(("Content-Length ",os.path.getsize(rpath)))
        result["headers"].append(("Last-Modified  ",os.path.getatime(rpath)))
        try:
            with open(rpath,"rt") as frd:
                for line in frd.readlines():
                    result["data"].append(line.encode("utf-8"))
        except IOError as exc:
            logs["static"](exc)
            try:
                with open(rpath,"rb") as frd:
                    result["data"] = frd.read()
            except Exception as exc:
                logs["static"](exc)
                result["data"] = None
        finally:
            logs["static"]("Resource had been prepared...")
        for header in reqheaders:
            if "Accept-Encoding"and "gzip" in header:
                F = True
            else:
                F = False
        if F:
            result["headers"].append(("Content-Encoding","gzip"))
            result["data"] = zlib.compress(mystr.concat(**{ "data": result["data"] }), 0)
        return result
    else:
        result["statusline"] = (404, cors.getmsgbycode(404).encode("utf-8"))
        for elem in cors.getheaders():
            result["headers"].append(elem)
        result["data"] = None
        logs["static"]("Resource is not found...")
        return result

def getstaticresources(**kwargs):
    """ This is the method for find static resources on root_path \
        by content types early defined on root_path in conf.json  

        kwargs:
                rootpath  - path to static content
                reqprops  - request properties contains all available info of current request reqline, \
                            method, host, port, version, path
    """
    rootpath  = kwargs.get("rootpath") 
    reqprops  = kwargs.get("reqprops") 
    logs["static"](" {0} {1}".format(rootpath, reqprops))

    mlen   = len(rootpath)
    rpath  = str()
    if rootpath[mlen-1:] != "/":
        rpath = mystr.concat(**{ "data": [rootpath, "/"] })
    else:
        rpath = rootpath

    response  = dict()
    fpath     = reqprops["path"]
    pos       = fpath.index(".")
    ctype     = fpath[pos+1:]

    rpath     = mystr.concat(**{ "data": [rpath, ctype] })
    rpath     = mystr.concat(**{ "data": [rpath, fpath] })
    response  = getdata(rpath, reqprops["headers"])
    return response["statusline"], response["headers"], response["data"]

def postmessage(**kwargs):
    datasz    = kwargs.get("datasz")       # int(self.headers['content-length'])
    reqdata   = kwargs.get("reqdata")      # post_data = self.rfile.read(content_len)
    reqprops  = kwargs.get("reqprops")     # request properties contains all available info of current request

    response  = dict()
    response["statusline"] = tuple()
    response["headers"]    = list()
    response["data"]       = list()

    msg   = """{ "elem": "text", "props": { "id": "idvalue","className": "value","name": "value" }, "content":[{ "id": "responsemessage","text": {textmsg} } ], "appto": null }"""
    table = """{ "elem": "table","props": { "id": "idvalue","className": "value","name": "value" }, "content": {trows}, "appto":null }"""

    logs["dynamic"]("httpserver post method")
    logs["dynamic"](reqprops)

    stepcors0 = cors["json"][0]
    stepcors1 = cors["json"][1]

    if datasz > 0:
        try:
            data = json.loads(reqdata.decode('utf-8'))
        except json.decoder.JSONDecodeError:
            data = reqdata.decode("utf-8")
        finally:
            response["headers"].append((200, getmsgbycode(200)))
            response["headers"].append((stepcors0,stepcors1))
            for item in cors.getheaders():
                response["headers"].append((item[0],item[1]))
            try:
                name  = data.get("name")        # name of configuration file in json format
                body  = data.get("body")        # file content of json file
                qkey  = data.get("qkey")        # query number in dbconfiguration description json file
                qargs = data.get("qargs")       # query argument`s values tuple 
            except KeyError as exc:
                print(exc)
            finally:
                if (name,body) != (None,None):
                    for each in ["table","form","list","block","text","textarea","combo","image","script"]:
                        if each in name.split("_"):
                            with open(name,"wt") as fw:
                                fw.writelines(body)
                if (name,body,qnum, qargs) == (None,None,None,None):
                    logs["httpserver"](data) # write that was received
                    requestmessages.put_nowait(("req", data))
                if (qkey,qargs) != (None,None):
                    resultset = self.dbprocessing(**data)
                    logs["httpserver"](data) # write that was received
                    response["headers"].append((200, getmsgbycode(200)))
                    response["headers"].append(stepcors0,stepcors1)
                    response["data"].append(table.format_map({ "trows": json.dumps(resultset)}).encode("utf-8"))
    else:
        logs["dynamic"]("content-length = %s".format(datasz))
        response["headers"].append((204,cors.getmsgbycode(204)))
        response["headers"].append(stepcors0,stepcors1)
        for item in cors.getheaders():
            response["headers"].append((item[0],item[1]))
        response["data"].append(msg.format_map({ "textmsg": "request was not accepted for processing, because message is epcent, length = {msglen}".format_map({"msglen": datasz}) }))
    response = bytes(repr(response),"utf-8")
    return response

def dbprocessing(**kwargs):
    res = list()
    qkey  = kwargs.get("qkey")
    qargs = kwargs.get("qargs")

    if tuple(dbconf.values()) != (None,None):
        lst = list("sqlite3", dbconf["dbpath"], querytemplates[qkey].format(qargs))
        logs["dbrequest"]((lst))
        db = ExecuteApp(**{
            "args": lst,
            "env": None,
            "wsgiapp": None
            })
        rs = db.worker() # list of strings
        for elem in rs:
            step = elem.split("\n")[0].split("|")
            step = (step)
            res.append(step)
    return res

def checkresponse(**kwargs):
    response = { "headers": list(),"data": list() }
    if kwargs.keys() == response.keys():
        if isinstance(kwargs.get("headers"), list) and isinstance(dct.get("data"), list):
            return True
        else:
            return False

def makeresponse(**kwargs):
    rootpath = kwargs.get("rpath")
    avctypes = kwargs.get("avctypes")
    host     = kwargs.get("host")
    port     = kwargs.get("port")
    kind     = kwargs.get("kind")

    logs["httpserver"]("{0},{1},{2},{3},{4} ".format(rootpath, avctypes, host, port, kind))

    class MinServer(CGIHTTPRequestHandler, SimpleHTTPRequestHandler):
        def getrequestprops(self):
            return {
                 "reqline": self.requestline,
                  "method": self.command,
                    "host": self.headers["HOST"].split(":")[0],
                    "port": self.headers["HOST"].split(":")[1],
                 "version": self.server_version,
                    "path": self.path,
                 "headers": self.headers.items()
            }

        def do_GET(self):
            logs["httpserver"]("do_GET begins")
            reqprops = self.getrequestprops()
            kwargs = { "rootpath": rootpath, "avctypes": avctypes, "reqprops": reqprops }
            logs["httpserver"](kwargs)
            step = getstaticresources(**kwargs)
            self.send_response(step[0][0],step[0][1])
            for hdr in step[1]:
                self.send_header(hdr[0],hdr[1])
            self.end_headers()
            if step[2] != None:
                for line in step[2]:
                    self.wfile.write(line)

        def do_POST(self):
            logs["httpserver"]("do_POST begins")
            rprops = self.getrequestprops()
            datasz = int(self.headers["content-length"])
            rdata  = self.rfile.read(int(self.headers["content-length"]))
            logs["httpserver"]((rprops, datasz, rdata))
            step = postmessage(**{ 
                "regprops": rprops,
                  "datasz": datasz,
                   "rdata": rdata })
            self.wfile.write(step)

    class CustomSMTPServer(smtpd.SMTPServer):
        self.smtpserverqueue = queue.Queue()
        self.dbschema   = "create table messages(id integer primary key autoincrement, remotehost text, mailfrom text, rcpttos text, data text);"
        self.insertinto = "insert into  messages(remotehost, mailfrom, rcpttos, data) values({0},{1},{2},{3});"

        def process_message(self, peer, mailfrom, rcpttos, data):
            smtpmsg = TextMessage(**{ "remotehost": peer, "sender": mailfrom,"receiver": rcpttos, "message": data })
            self.smtpserverqueue.put_nowait(smtpmsg)
            logs["smtpserver"]((peer, mailfrom, rcpttos, data))

        def __call__(self):
            while(self.smtpserverqueue.empty() != True):
                kwargs = self.smtpserverqueue.get()
                values = list(kwargs.values())
                self.insertinto.format(values)
                lst = list("sqlite3", dbconf["dbpath"], self.insertinto)
                ExecuteApp(**{ "args": lst, "env": None, "wsgiapp": None })

    if kind == "smtp":
        CustomSMTPServer(**kwargs)()
    elif kind == "http":
        try:
            print("Starting httpd...\n")
            logs["httpserver"]("Starting httpd...\n")
            server_address = (host, port)
            httpd = HTTPServer(server_address, MinServer)
            httpd.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
            httpd.serve_forever()
        except KeyboardInterrupt:
            httpd.server_close()
            logs["httpserver"]("Stopping httpd...\n")

"""
WSGIVARIABLES = [ "REQUEST_METHOD","SCRIPT_NAME","PATH_INFO","QUERY_STRING","CONTENT_TYPE","CONTENT_LENGTH","SERVER_NAME","SERVER_PORT","SSL_PROTOCOL","DOCUMENT_ROOT","PATH_TRANSLATED",
                  "wsgi.version","wsgi.input","wsgi.url_scheme","wsgi.errors","wsgi.multithread","wsgi.multiprocess","wsgi.run_once"]
"""

class WSGIProxy(CGIHTTPRequestHandler, SimpleHTTPRequestHandler):
    def do_GET(self):
        self.proxy()
    def do_POST(self):
        self.proxy()

    def proxy(self):
        logs["wsgiserver"]("proxy method was invoked")
        self.setwsgienv()
        self.invokewsgiapp()

    def setwsgienv(self):
        self.wsgienv["SERVER_PROTOCOL"] = "HTTP/1.1"
        self.wsgienv["SERVER_NAME"]     = self.reqHandler.headers["HOST"].split(":")[0]
        self.wsgienv["SERVER_PORT"]     = self.reqHandler.headers["HOST"].split(":")[1]
        self.wsgienv["REQUEST_METHOD"]  = self.reqHandler.command
        self.wsgienv["QUERY_STRING"]    = self.reqHandler.requestline
        self.wsgienv["CONTENT_TYPE"]    = self.reqHandler.headers["Content-Type"]
        self.wsgienv["CONTENT_LENGTH"]  = int(self.reqHandler.headers["Content-Length"])
        self.wsgienv["SCRIPT_NAME"]     = self.reqHandler.headers["SCRIPT_NAME"]

        if self.wsgienv["REQUEST_METHOD"] in ["POST","post"]:
            val = self.wsgienv["CONTENT_LENGTH"]
            if val > 0:
                post_data = self.reqHandler.rfile.read(val)
                try:
                    post_data = json.loads(post_data.decode('utf-8'))
                except json.decoder.JSONDecodeError:
                    post_data = post_data.decode("utf-8")
                finally:
                    logs["dynamic"](post_data)
                    self.wsgienv["wsgi.input"] = post_data
            else:
                logs["dynamic"]("content-length = %s", val)
                self.reqHandler.wfile.write(getmsgbycode(204))

        elif self.wsgienv["REQUEST_METHOD"] in ["GET","get"]:
            lastindex = self.path.rfind("/",0,len(self.path))+1
            for ctype in config.avctypes:
                regexp = "/*.{0}$".format(ctype)
                logs["dynamic"](regexp)
                if re.search(regexp,self.path) != None:
                    rpath = operator.concat(config.root_path,operator.concat(ctype,"/"))
                    rpath = operator.concat(rpath,self.path[lastindex:len(self.path)])
                    self.wsgienv["PATH_INFO"] = rpath
                    logs["dynamic"](rpath)

    def invokewsgiapp(self):
        """ method invokes wsgi external app
            1) when wsgiapp works on host and port we send it requests from wsgiproxy
            2) when wsgiapp does not work yet we must to start it
        """
        if os.path.exists(self.tmpfile):
            ctypes = CORSSettings.ctypes["json"]
            if self.wsgienv["REQUEST_METHOD"] == "POST" and self.wsgienv.get("wsgi.input") != None:
                kwargs = {
                        "headers": { ctypes[0]: ctypes[1] },
                        "host": self.wsgienv["SERVER_NAME"],
                        "port": self.wsgienv["SERVER_PORT"],
                        "url":  self.requestline,
                        "body": self.wsgienv.get("wsgi.input")
                        }
                response = Request.httprequest(**kwargs)
            elif self.wsgienv["REQUEST_METHOD"] == "GET":
                kwargs = {
                        "host": self.wsgienv["SERVER_NAME"],
                        "port": self.wsgienv["SERVER_PORT"],
                        "url":  self.requestline,
                        "headers": { ctypes[0]: ctypes[1] },
                        }
                response = Request.httprequest(**kwargs)
            else:
                kwargs = {
                        "args": ("python3.5 ", self.wsgienv["SCRIPT_NAME"]),
                        "wsgiapp": True,
                        "env": self.wsgienv
                        }
                app = ExecuteApp(**kwargs)
                self.response = app.runwsgi()
                with open(self.tmpfile,"wt") as pidfile: 
                     pidfile.writelines(app.pid)
        if checkresponse(**self.response):
            return response

    def start_response(self, status, response_headers, exc_info=None):
        """'start_response()' callable as specified by PEP 3333"""
        self.status = status
        self.headers = response_headers
        if exc_info: 
            raise Exception
        return self.write((self.status,self.headers))

    def write(self, data):
        """'write()' callable as specified by PEP 3333"""
        out = sys.stdout.buffer
        try:
            if isinstance(data,tuple) and isinstance(data[0], str) and isinstance(data[1], list):
                out.write(bytes("Status: {0}".format(data[0], "utf-8")))
                for header in data[1]:
                    out.write(bytes(header,"utf-8"))
                    out.write(bytes("\r\n","utf-8"))
                    out.write(bytes(data,"utf-8"))
                    out.flush()
            elif isinstance(data, bytes) or isinstance(data, str):
                out.write(data.encode("utf-8"))
        except ValueError as exc:
            print(exc)

class WSGIApp:
    def __init__(self, env, callback):
        self.getqueue  = queue.Queue()
        self.postqueue = queue.Queue()
        self.env = env
        self.responser = callback

    def urlreconstruction(self):
        """ PEP 3333 WSGI Specification """
        wsgi_url_scheme = concat(self.env["wsgi.url_scheme"],"://")

        if self.env.get("HTTP_HOST"):
            wsgi_url_scheme = concat(wsgi_url_scheme, self.env["HTTP_HOST"])
        else:
            wsgi_url_scheme = concat(wsgi_url_scheme, self.env["SERVER_NAME"])

        if wsgi.url_scheme == "https":
            if self.server_port == "443" or self.server_port == "81":
                wsgi_url_scheme = concat(wsgi_url_scheme, ":")
                wsgi_url_scheme = concat(wsgi_url_scheme, self.server_port)

        wsgi_url_scheme = concat(wsgi_url_scheme, quote(self.script_name))
        wsgi_url_scheme = concat(wsgi_url_scheme, quote(self.path_info))

        if self.query_string:
            wsgi_url_scheme = concat(wsgi_url_scheme,"?")
            wsgi_url_scheme = concat(wsgi_url_scheme, self.query_string)

        return wsgi_url_scheme

    def escapevalues(self, dct=dict):
        if self.wsgiapp:
            for key in list(dct.keys()):
                if isinstance(dct[key],str):
                    return escape(dct.get(key,[''])[0]) # Always escape user input to avoid script injection
                elif isinstance(dct[key],list):
                    return [escape(x) for x in dct.get(key,[])] # Always escape user input to avoid script injection

    def getwsgienv(self, env):
        self.request_method    = env.get("REQUEST_METHOD")
        self.script_name       = env.get("SCRIPT_NAME")
        self.path_info         = env.get("PATH_INFO")
        self.query_string      = env.get("QUERY_STRING")
        self.content_type      = env.get("CONTENT_TYPE")
        self.server_name       = env.get("SERVER_NAME")
        self.server_port       = env.get("SERVER_PORT")
        self.ssl_protocol      = env.get("SSL_PROTOCOL")
        self.http_host         = env.get("HTTP_HOST")
        self.document_root     = env.get("DOCUMENT_ROOT")
        self.path_translated   = env.get("PATH_TRANSLATED")
        self.wsgi_version      = env.get("wsgi.version")
        self.wsgi_url_scheme   = self.urlreconstruction()
        self.wsgi_multithread  = env.get("wsgi.multithread")
        self.wsgi_multiprocess = env.get("wsgi.multiprocess")
        self.wsgi_run_once     = env.get("wsgi.run_once")

        if self.request_method == "GET":
            self.content_length = 0
            if self.query_string == None:
                step = {
                        "qstring":  None,
                        "rootpath": self.wsgi_url_scheme,
                        "avctypes": self.content_type
                        }
                self.getqueue["req"] = step
            else:
                step = {
                        "qstring":  self.escapevalues(parse_qs(self.query_string)),
                        "rootpath": self.wsgi_url_scheme,
                        "avctypes": self.content_type
                        }
                self.getqueue["req"] = step

        elif self.request_method == "POST":
            self.content_length = int(self.env.get("CONTENT_LENGTH"))
            post_data = self.env.get("wsgi.input")
            if type(post_data) == str:
                step = {
                        "qstring":  self.escapevalues(parse_qs(post_data.read(self.content_length))),
                        "rootpath": self.wsgi_url_scheme,
                        "avctypes": self.content_type
                        }
                self.postqueue["req"] = step
            elif type(post_data) == bytes:
                step = {
                        "qstring":  post_data.decode("utf-8"),
                        "rootpath": self.wsgi_url_scheme,
                        "avctypes": self.content_type
                        }
                self.postqueue["req"] = step

    def getprocessing(self):
        getresults  = list()
        while(self.getqueue["req"].empty() != True):
            step = self.getqueue["req"]
            if step.get("qstring") == None:
                kwargs = {
                        "rootpath": step.get("rootpath"),
                        "avctypes": step.get("avctypes")
                        }
                getresults.append(getstaticresources(**kwargs))
            else:
                kwargs = {
                        "qstring":  step.get("qstring"),
                        "rootpath": step.get("rootpath"),
                        "avctypes": step.get("avctypes")
                        }
                getresults.append(postmessage(**kwargs))

        return (getresults, postresults)

    def __call__(self):
        self.getwsgienv(env)
        self.getprocessing()

