# A simple HTTP server which counts the number of calls it handled and return
# them when using the /count url.
import sys
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer


COUNT = 0


class CounterHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        global COUNT

        if self.path == '/count':
            self.wfile.write(COUNT)
            return
        else:
            COUNT += 1
            self.wfile.write("yeah")
            return


def main(port=8000):
    httpd = HTTPServer(('', port), CounterHandler)
    httpd.serve_forever()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "This script should be called with the port as an argument"
        sys.exit(1)
    main(int(sys.argv[1]))
