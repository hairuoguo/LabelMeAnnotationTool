!/usr/bin/python
from __future__ import print_function
import threading
from OpenSSL import SSL
from flask import Flask, request, current_app, make_response


app = Flask(__name__)
@app.route("/hello_world")
def hello_world():
    return "Hello world!"
    
    
if __name__ == "__main__":
   app.run(threaded=True)
