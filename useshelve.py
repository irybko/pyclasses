# -*- utf-8 -*-
##########################################
# PSF license aggrement for useshelve.py
# Developed by Ivan Rybko
# UseShelve

import shelve
from threading import Lock
#
class UseShelve:
    def __init__(self, dbpath=str):
        self.db = shelve.open(dbpath)

    def task(self, **kwargs):
        try:
            record_key  = kwargs.get("primary_key")
            dbpath      = kwargs.get("dbpath")
            action      = kwargs.get("task")
            value       = kwargs.get("value")
        except KeyError as err:
            print(err)
        finally:
            mutex = Lock()
            mutex.acquire()
            if action == "insert":
                with shelve.open(dbpath) as conn:
                    if record_key not in list(conn.keys()):
                        conn[record_key] = value
            elif action == "read":
                with shelve.open(dbpath) as conn:
                    if record_key in list(conn.keys()):
                        return conn[record_key]
            elif action == "update":
                with shelve.open(dbpath) as conn:
                    if record_key in list(conn.keys()):
                        temp = conn[record_key]
                        temp.append(value)
                        conn[record_key] = temp
            elif action == "delete":
                with shelve.open(dbpath) as conn:
                    if record_key in list(conn.keys()):
                        del conn[record_key]
            mutex.release()
