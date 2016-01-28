from http.server import HTTPServer
from http.server import CGIHTTPRequestHandler

Port = 8000
Handler = CGIHTTPRequestHandler
HttpServer = HTTPServer(("localhost", Port), Handler)

HttpServer.serve_forever()
