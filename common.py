# -*- utf-8 -*-
######################################
# PSF license aggrement for common.py
# Developed by Ivan Rybko
######################################

from http.server import HTTPServer, CGIHTTPRequestHandler, SimpleHTTPRequestHandler
import smtpd
import os
from corsettings import CORSSettings
from extstring import ExtString
from logmsg import Logs
#
cors = CORSSettings()
#
mystr = ExtString()
#
def concat(s1,s2):
    res = str()
    res = res.__add__(s1)
    res = res.__add__(s2)
    return res
#
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


