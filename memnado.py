import functools
import socket

from tornado.ioloop import IOLoop
from tornado.iostream import IOStream

class Memnado(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        s.connect((self.host, self.port))
        self.stream = IOStream(s)
    
    def set(self, key, value, expiry=0, callback=lambda d: d):
        content_length = len(value)
        self.stream.write("set %s 1 %s %s\r\n%s\r\n" % (key, expiry, 
                        content_length, value))
        self.stream.read_until("\r\n", callback)
    
    def get(self, key, callback):
        def process_get(stream, cb, data):
            status, k, flags, content_length = data.strip().split(' ')
            stream.read_bytes(int(content_length), functools.partial(cb, stream))
        
        self.stream.write("get %s\r\n" % key)
        self.stream.read_until("\r\n", functools.partial(process_get, self.stream, callback))


if __name__ == '__main__':
    def do_stuff(stream, data):
        print "I made it! %s" % data

    m = Memnado("127.0.0.1", 11211)
    m.get("hey", do_stuff)

    IOLoop.instance().start()

