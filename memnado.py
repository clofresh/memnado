import functools
import socket
from base64 import b64encode, b64decode

from tornado.ioloop import IOLoop
from tornado.iostream import IOStream

class Memnado(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        s.connect((self.host, self.port))
        self.stream = IOStream(s)
    
    def set(self, key, value, callback, expiry=0):
        key = b64encode(key)
        value = b64encode(value)
        content_length = len(value)
        self.stream.write("set %s 1 %s %s\r\n%s\r\n" % (key, expiry, 
                        content_length, value))
        self.stream.read_until("\r\n", callback)
    
    def get(self, key, callback):
        key = b64encode(key)
        
        def process_get(stream, cb, data):
            if data[0:3] == 'END': # key is empty
                cb(None)
            else:
                status, k, flags, content_length = data.strip().split(' ')
                
                def wrapped_cb(f):
                    return lambda data: f(b64decode(data))
                
                stream.read_bytes(int(content_length), wrapped_cb(cb))
                stream.read_until("\r\nEND\r\n", lambda d: d)
        
        self.stream.write("get %s\r\n" % key)
        self.stream.read_until("\r\n", functools.partial(process_get, self.stream, callback))



