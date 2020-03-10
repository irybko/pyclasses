# -*- utf-8 -*-
#########################################
# PSF license aggrement for wsgiproxy.py
# Developed by Ivan Rybko
# WSGIProxy
#########################################
"""
WSGIVARIABLES = [ "REQUEST_METHOD","SCRIPT_NAME","PATH_INFO","QUERY_STRING","CONTENT_TYPE","CONTENT_LENGTH","SERVER_NAME","SERVER_PORT","SSL_PROTOCOL","DOCUMENT_ROOT","PATH_TRANSLATED",
                  "wsgi.version","wsgi.input","wsgi.url_scheme","wsgi.errors","wsgi.multithread","wsgi.multiprocess","wsgi.run_once"]
"""

from http.server import SimpleHTTPRequestHandler, CGIHTTPRequestHandler
import operator
import os
import sys

#
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
