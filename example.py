from datetime import datetime

import tornado.httpserver
import tornado.ioloop
import tornado.web
from tornado.web import asynchronous

import memnado

m = memnado.Memnado('127.0.0.1', 11211)

class MainHandler(tornado.web.RequestHandler):
    key = 'data'

    @asynchronous
    def post(self):
        data = self.get_argument('data', '')

        def set_it(response):
            self.write('Saved %s. <a href="/">View it.</a>' % data)
            self.finish()
        
        now = datetime.today().isoformat()

        to_store = "%s: %s" % (now, str(data))

        m.set(self.key, to_store, self.async_callback(set_it))

    @asynchronous
    def get(self):
        def do_it(data):
            self.write("<pre>%s</pre>" % str(data))
            self.finish()
        
        self.write("""
            <form action="/" method="post">
              <label>Set some data: </label>
              <input name="data" value="" />
              <input type="submit" />
            </form>
            <br />
        """)
        self.write("Current data: ")
        m.get(self.key, self.async_callback(do_it))
                

application = tornado.web.Application([
    (r"/", MainHandler)
])

if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
