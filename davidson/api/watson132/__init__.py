#!/usr/bin/env python
from datetime import datetime
from pprint import pprint as dump
from pathlib import Path
from socket import gethostbyaddr
import tornado.web
import tornado.httpserver
import tornado.ioloop
import tornado.options
import requests, json, functools
from tornado.options import define, options
from tornado.escape import json_encode, json_decode

# base class used by all handlers
class BaseHandler(tornado.web.RequestHandler):
    def initialize(self, hosts):
        # copy reference to passed `hosts` object
        self.hosts = hosts
        
        ## the Session() we'll use to make requests
        self.sess = requests.Session()

        ## setup any client TLS/SSL info provided
        ca, cert, key = [
            getattr(options, f'client_{t}', None)
            for t in ['ca','key','cert']
        ]

        # process `ca` to see if there's anything of value
        if ca:
            if Path(ca).is_file():
                self.sess.verify = ca

        # process `cert` & `key` to ...
        if cert and not key:
            if Path(cert).is_file():
                self.sess.cert = cert
            else:
                raise FileNotFoundError(cert)
        elif cert and key:
            if Path(cert).is_file() and Path(key).is_file():
                self.sess.cert = (cert, key)
            else:
                raise FileNotFoundError(cert,key)
            
        # retrun to our regularly scheduled program
        return
            
    def write_json(self, obj):
        self.add_header('Content-Type', 'application/json')
        self.write(json_encode(obj))
        return

    def write_result(self, result=None):
        obj={'error': 0}
        if result:
            obj['data']=result
            pass        
        self.write_json(
            obj
        )
        return
    
    def error_json(self, message):
        self.write_json(
            {
                'data': message,
                'error': 1
            }
        )
        return

    pass


# handler for lab machine information end-points
class MachineHandler(BaseHandler):
    async def get(self):
        """produce & output json object with sanitized information 
        stored about requesting client"""
        self.write_result({})
        return
    
    async def post(self):
        """update information associated with requesting 
        client using request body"""

        # ensure request body content-type is acceptable 
        if not self.request.headers['Content-Type'].endswith('application/json'):
            self.error_json("Unsupported content-type")
            return

        # verify parsable is valid json
        try:
            obj = json_decode(self.request.body)
        except:
            self.error_json("Error parsing request body")
            return

        # retrive remote ip address (TODO: add trust forward-headers option)
        #  and update data associated with client
        remote_ip = self.request.headers.get('X-Forwarded-For') or \
            self.request.remote_ip 
        self.hosts[remote_ip] = obj
        self.hosts[remote_ip]['timestamp'] = datetime.now()

        # indicate success to clients
        self.write_result()
        return
    
    pass    

# generate and return simple object summarizing status of machines in the lab
class StatusHandler(BaseHandler):
    async def get(self):
        now = datetime.now()

        obj=dict()
        for ipaddr,data in self.hosts.items():
            tag = data.get('tag')
            entry = {
                'tag': tag,
                'ip': ipaddr,
                'system': data.get('system', 'Unknown'),
                'timestamp': data['timestamp']
            }

            # if `tag` hasn't been seenm, or `entry` is more recent than
            #  the existing value of `obj[tag]`, we update/set obj[tag] 
            if (not tag in obj) or (obj[tag]['timestamp'] < entry['timestamp']):
                if 'users' in data:
                    entry['users'] = 0
                    for user in data['users']:
                        if user['uid'] > 999:
                            entry['users']+=1
                
                obj[tag]=entry
                pass

        # post-processing
        for tag, entry in obj.items():
            # relabel machines which haven't checked in recently
            if (now - entry['timestamp']).total_seconds() > 10*60.0:
                entry['system'] = 'Off'
                if 'users' in entry:
                    del entry['users']
                    
            # convert timestamp to string
            entry['timestamp']=entry['timestamp'].isoformat()

        # return serialized list of values
        self.write_json(list(obj.values()))
        return 
    
    pass


# tornado appliation
def make_app():
    hosts=dict()
    return tornado.web.Application(
        [
            (r"/api/status", StatusHandler, dict(hosts=hosts)),
            (r"/api/machine", MachineHandler, dict(hosts=hosts))
        ]
    )
