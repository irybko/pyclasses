# -*- utf-8 -*-
########################################
# PSF license aggrement for ini.py
# Developed by Ivan Rybko
# Ini
########################################

from configparser import ConfigParser

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
