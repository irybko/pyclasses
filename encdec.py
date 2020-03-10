# -*- utf-8 -*-
########################################
# PSF license aggrement for encdec.py
# Developed by Ivan Rybko
# EncDec
########################################
import time

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
