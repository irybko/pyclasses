# -*- utf-8 -*-
#########################################
# PSF license aggrement for localtime.py
# Developed by Ivan Rybko
# LocalTime
#########################################

import time
import datetime
import locale
#
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
