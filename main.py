from http.server import HTTPServer
from http.server import CGIHTTPRequestHandler

import logging

logging.basicConfig(level=logging.DEBUG)

Port = 8000
Handler = CGIHTTPRequestHandler
HttpServer = HTTPServer(("localhost", Port), Handler)

logging.info("Starting keyring on port {}".format(Port))

HttpServer.serve_forever()
