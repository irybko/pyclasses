# -*- utf-8 -*-
########################################
# PSF license aggrement for singeton.py
# Developed by Ivan Rybko
# Singleton
########################################

class Singleton:
    def __init__(self, aClass):
        self.aClass = aClass
        self.instance = None
    def __call__(self, *args, **kwargs):
        if self.instance == None:
            self.instance = self.aClass(*args, **kwargs)
        return self.instance
