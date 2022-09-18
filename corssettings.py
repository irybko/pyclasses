# -*- utf-8 -*-
#############################################
# PSF license aggrement for corssettings.py
# Developed by Ivan Rybko
#############################################

from singleton  import Singleton
from logmsg    import Logmsg
from extstring import ExtString
from extdict   import ExtDict
import queue

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


