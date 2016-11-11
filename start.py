import tornado.ioloop
import tornado.web
import tornado.httpserver
import tornado.process
import video
import gen
import os


cam = None
html_page_path = dir_path = os.path.dirname(os.path.realpath(__file__)) + '/www'


class HtmlPageHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self, file_name='index.html'):
        # fill header fields
        self.set_header('Connection', 'close')
        self.set_header('Content-Type', 'text/html')

        # format path to page
        index_page = os.path.join(html_page_path, file_name)
        if os.path.exists(index_page):
            page = open(index_page)
            payload = page.read()
            page.close()
        else:
            self.write('<a>Sorry, but page not found</a>')

        self.write(payload)
        self.flush()


class SetParamsHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def post(self):
        #print self.request.body
        # get args from POST request
        width = int(self.get_argument('width'))
        height = int(self.get_argument('height'))
        # try to change resolution
        try:
            cam.set_resolution(width, height)
            self.write({'resp': 'ok'})
        except:
            self.write({'resp': 'bad'})


class StreamHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        """
        functionality: generates GET response with mjpeg stream
        input: None
        :return: yields mjpeg stream with http header
        """
        # Set http header fields
        self.set_header('Cache-Control',
                         'no-store, no-cache, must-revalidate, pre-check=0, post-check=0, max-age=0')
        self.set_header('Connection', 'close')
        self.set_header('Content-Type', 'multipart/x-mixed-replace;boundary=--boundarydonotcross')

        while True:
            # Generating images for mjpeg stream and wraps them into http resp
            img = cam.get_frame()
            self.write("--boundarydonotcross\n")
            self.write("Content-type: image/jpeg\r\n")
            self.write("Content-length: %s\r\n\r\n" % len(img))
            self.write(str(img))
            yield tornado.gen.Task(self.flush)


def make_app():
    # add handlers
    return tornado.web.Application([
        (r'/', HtmlPageHandler),
        (r'/video_feed', StreamHandler),
        (r'/setparams', SetParamsHandler),
        (r'/(?P<file_name>[^\/]+htm[l]?)+', HtmlPageHandler),
        (r'/(?:image|css|js)/(.*)', tornado.web.StaticFileHandler, {
                                                                 'path': './image',
                                                                 'path': './css',
                                                                 'path': './js'
                                                                })
    ])


if __name__ == "__main__":
    # creates camera
    cam = video.UsbCamera()
    # bind server on 8080 port
    sockets = tornado.netutil.bind_sockets(8080)
    server = tornado.httpserver.HTTPServer(make_app())
    server.add_sockets(sockets)
    tornado.ioloop.IOLoop.current().start()
