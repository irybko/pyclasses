# -*- utf-8 -*-
########################################
# PSF license aggrement for wsgiapp.py
# Developed by Ivan Rybko
# WSGIApp
########################################

import queue
from operator import concat 

class WSGIApp:
    def __init__(self, env, callback):
        self.getqueue    = queue.Queue()
        self.postqueue   = queue.Queue()
        self.env         = env
        self.responser   = callback
        self.server_port = ""

    def urlreconstruction(self):
        """ PEP 3333 WSGI Specification """
        wsgi_url_scheme = concat(self.env["wsgi.url_scheme"],"://")

        if self.env.get("HTTP_HOST"):
            wsgi_url_scheme = concat(wsgi_url_scheme, self.env["HTTP_HOST"])
        else:
            wsgi_url_scheme = concat(wsgi_url_scheme, self.env["SERVER_NAME"])

        if wsgi_url_scheme == "https":
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

