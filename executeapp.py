# -*- utf-8 -*-
###########################################
# PSF license aggrement for executeapp.py
# Developed by Ivan Rybko
# ExecuteApp
###########################################

from wsgiref.simple_server import make_server
import subprocess
import os


#
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
