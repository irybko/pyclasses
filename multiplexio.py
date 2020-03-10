# -*- utf-8 -*-
###############################################################
# PSF license aggrement for multiplexio.py
# Developed by Ivan Rybko
# MultiplexIO, HTTPNode, HTTPServerNode, HTTPClientNode classes
################################################################

import select
import multiprocessing
import queue

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


class HTTPServerNode(HTTPNode):
    def __init__(self, **kwargs):
        kwargs["role"] = "server"
        HTTPNode.__init__(self, **kwargs)

class HTTPClientNode(HTTPNode):
    def __init__(self, **kwargs):
        kwargs["role"] = "client"
        HTTPNode.__init__(self, **kwargs)
