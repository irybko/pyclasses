# -*- utf-8 -*-
###########################################
# PSF license aggrement for usesmtpimap.py
# Developed by Ivan Rybko
###########################################

import email
import smtplib, smtpclient
import base64
import imaplib

class TextMessage:
    """
        Create a message for an email.
        from:         Email address of the sender.
        to:           Email address of the receiver.
        subject:      The subject of the email message.
        message_text: The text of the email message.
    """
    def __init__(self, **kwargs):
        self.keys  = ["sender","receiver","subject","message","addition"]
        self.outer = ReqRes
        if kwargs != None and list(kwargs.keys()) == self.keys:
            for k in kwargs:
                self.__setattr__(k, kwargs.get(k))

    def __repr__(self, msg):
        return base64.urlsafe_b64encode(self.__dict__.as_string())

    def __setattr__(self, attr, value):
        assert attr in self.keys, " not allowed"
        if attr == "sender":      self.__dict__["From"]     = value
        elif attr == "receiver":  self.__dict__["To"]       = value
        elif attr == "subject":   self.__dict__["Subject"]  = value
        elif attr == "message":   self.__dict__["Message"]  = smtplib.MIMEText(value)
        elif attr == "addition":
            if isinstance(value,dict):
                kwargs = {
                    "rootpath": value.get("rootpath"),
                    "avctypes": value.get("avctypes")
                    }
                self.__dict__["resources"] = getstaticresources(**kwargs)

    def __getattr__(self, attr):
        assert attr in self.keys, " not allowed"
        if attr == "sender":     return self.__dict__["From"]
        elif attr == "receiver": return self.__dict__["To"]
        elif attr == "subject":  return self.__dict__["Subject"]
        elif attr == "message":  return self.__dict__["Message"]
        elif attr == "addition": return self.__dict__["resources"]

class IMAPClient:
    def __init__(self, **kwargs):
        self.servername = kwargs.get("host")
        self.serverport = kwargs.get("port")
        self.ssl        = kwargs.get("ssl")
        self.username   = kwargs.get("username")
        self.password   = kwargs.get("password")
        self.address    = kwargs.get("address")

        logs["imapclient"](repr(self))

        try:
            if self.ssl: self.conn = imaplib.IMAP4_SSL(self.servername)
            else:        self.conn = imaplib.IMAP4(self.servername)
        except Exception as exc:
            print(exc)
        finally:
            self.conn.login(self.username, self.password)
            self.imapqueue = queue.Queue()

    def __del__(self):
        self.conn.close()
        self.conn.logout()

    def imapsumm(self):
        self.conn.select('Inbox')
        step = self.conn.search(None, 'ALL')
        step = step[1]
        return sum(num for num in step[0].split())

    def imapgetone(self, num):
        self.conn.select('Inbox')
        status, data = self.conn.fetch(str(num), "(RFC822)")
        self.email_message = email.message_from_string(data[0][1])
        self.imapqueue["req"] = self.email_message

    def imapremoveone(self, num):
        self.conn.select("Inbox")
        self.conn.store(num, '+FLAGS', r'\Deleted')
        self.conn.expunge()

    def imapremoveall(self):
        maxlen = self.imapsumm()
        num = 0
        while(num<=maxlen):
            self.imapremoveone(num)
            num += 1

    def imapgetlatestemailsentto(self):
        timeout=300
        poll=1
        start_time = time.time()
        while ((time.time() - start_time) < timeout):
            status, data = self.conn.select('Inbox')
            if status != 'OK':
                time.sleep(poll)
            continue
            status, data = self.conn.search(None, 'TO', self.address)
            data = [d for d in data if d is not None]
            if status == 'OK' and data:
                for num in reversed(data[0].split()):
                    status, data = self.conn.fetch(num, '(RFC822)')
                    email_msg = email.message_from_string(data[0][1])
                    self.imapqueue["req"] = email_msg
            time.sleep(poll)
            raise AssertionError("No email sent to {0} found in inbox after polling for {1} seconds.".format(email_address, timeout))

    def imapremovemsgssentto(self):
        self.conn.select('Inbox')
        status, data = self.conn.search(None, 'TO', self.address)
        if status == 'OK':
            for num in reversed(data[0].split()):
                status, data = self.conn.fetch(num, '(RFC822)')
                self.conn.store(num, '+FLAGS', r'\Deleted')
                self.conn.expunge()

class Request:
    def httprequest(**kwargs):
        host    = kwargs.get("host")
        port    = kwargs.get("port")
        reqtype = kwargs.get("reqtype")
        headers = kwargs.get("headers")
        url     = kwargs.get("url")

        logs["httpclient"]((host, port, reqtype, headers, url))

        response = dict().fromkeys(["status","headers","reason","body"])

        if reqtype == "get":
            try:
                conn = HTTPConnection(host,port)
                conn.request("GET", url, headers)
            except Exception as exc:
                print(exc)
            finally:
                rdata = conn.getresponse()
                rheaders = rdata.getheaders()
                rbody = str()
                step = [elem for elem in rheaders if "Content-Length" in elem]
                datasz = int(step[0][1])
                rbody  = rdata.read(datasz).decode("utf-8")

                logs["httpclient"]("== get method data==")
                logs["httpclient"]((rdata, rheaders, rbody))

                response["status"]   = rdata.status
                response["headers"]  = rheaders
                response["reason"]   = rdata.reason
                response["body"]     = rbody

                conn.close()
                return response

        elif reqtype == "post":
            body = kwargs.get("body")
            try:
                conn = HTTPConnection(host,port)
                conn.request("POST", url, body, headers)
            except Exception as exc:
                print(exc)
            finally:
                rdata = conn.getresponse()
                respheaders = rdata.getheaders()

            return { 
                "status":  rdata.status,
                "headers": respheaders,
                "reason":  rdata.reason 
                }
            conn.close()

            logs["httpclient"]("== post method data ==")
            logs["httpclient"]((rdata, respheaders, respbody))


    def smtprequest(**kwargs):
        host  = kwargs.get("host")
        port  = kwargs.get("port")
        message = kwargs.get("message")


        logs["smtpclient"]("== smtp request data==")
        logs["smtpclient"]((rdata, respheaders, respbody))

        if isinstance(message, TextMessage):
            if message.sender != None and message.receiver != None and message.subject  != None and message.message  != None:
                smtpclient = smtplib.SMTP((host,port))
                smtpclient.set_debuglevel(True)  # show communication with the server
                try:
                    smtpclient.sendmail(message.sender,message.receiver,message.subject,message.message)
                except SMTPException as exc:
                    print(exc)
                finally:
                    smtpclient.quit()

    def imaprequest(**kwargs):
        action = kwargs.get("action")
        number = kwargs.get("number")

        logs["imapclient"]("== smtp request data==")
        logs["imapclient"]((rdata, respheaders, respbody))

        imapclient = IMAPClient(**kwargs)

        if action == "imapsumm":                        return imapclient.imapsumm()
        elif action == "imaprmvone" and instance(number,int):  imapclient.imapremoveone(number)
        elif action == "imaprmvall":                           imapclient.imapremoveall()
        elif action == "imapgetone":                    return imapclient.imapgetone(number)
        elif action == "imapgetlatestemailsentto":             imapclient.imapremovemsgssentto()
        elif action == "imapremovemsgssentto":                 imapclient.imapremovemsgssentto()


