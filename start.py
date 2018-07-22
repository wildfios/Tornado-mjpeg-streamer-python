import time

import tornado.ioloop
import tornado.web
import tornado.httpserver
import tornado.process
import tornado.template
import video
import gen
import os


cam = None
html_page_path = dir_path = os.path.dirname(os.path.realpath(__file__)) + '/www/'


class HtmlPageHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self, file_name='index.html'):
        # Check if page exists
        index_page = os.path.join(html_page_path, file_name)
        if os.path.exists(index_page):
            # Render it
            self.render('www/' + file_name)
        else:
            # Page not found, generate template
            err_tmpl = tornado.template.Template("<html> Err 404, Page {{ name }} not found</html>")
            err_html = err_tmpl.generate(name=file_name)
            # Send response
            self.finish(err_html)


class SetParamsHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def post(self):
        # print self.request.body
        # get args from POST request
        width = int(self.get_argument('width'))
        height = int(self.get_argument('height'))
        # try to change resolution
        try:
            cam.set_resolution(width, height)
            self.write({'resp': 'ok'})
        except:
            self.write({'resp': 'bad'})
            self.flush()
            self.finish()


class StreamHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        ioloop = tornado.ioloop.IOLoop.current()

        self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, pre-check=0, post-check=0, max-age=0')
        self.set_header( 'Pragma', 'no-cache')
        self.set_header( 'Content-Type', 'multipart/x-mixed-replace;boundary=--jpgboundary')
        self.set_header('Connection', 'close')

        self.served_image_timestamp = time.time()
        my_boundary = "--jpgboundary"
        while True:
            # Generating images for mjpeg stream and wraps them into http resp
            if self.get_argument('fd') == "true":
                img = cam.get_frame(True)
            else:
                img = cam.get_frame(False)
            interval = 0.1
            if self.served_image_timestamp + interval < time.time():
                self.write(my_boundary)
                self.write("Content-type: image/jpeg\r\n")
                self.write("Content-length: %s\r\n\r\n" % len(img))
                self.write(img)
                self.served_image_timestamp = time.time()
                yield tornado.gen.Task(self.flush)
            else:
                yield tornado.gen.Task(ioloop.add_timeout, ioloop.time() + interval)


def make_app():
    # add handlers
    return tornado.web.Application([
        (r'/', HtmlPageHandler),
        (r'/video_feed', StreamHandler),
        (r'/setparams', SetParamsHandler),
        (r'/(?P<file_name>[^\/]+htm[l]?)+', HtmlPageHandler),
        (r'/(?:image)/(.*)', tornado.web.StaticFileHandler, {'path': './image'}),
        (r'/(?:css)/(.*)', tornado.web.StaticFileHandler, {'path': './css'}),
        (r'/(?:js)/(.*)', tornado.web.StaticFileHandler, {'path': './js'})
        ],
    )


if __name__ == "__main__":
    # creates camera
    cam = video.UsbCamera()
    # bind server on 8080 port
    app = make_app()
    app.listen(9090)
    tornado.ioloop.IOLoop.current().start()
