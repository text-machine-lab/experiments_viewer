import json

from bottle import Bottle, HTTPError, request, template, route, static_file, view, redirect


# app and routers
app = Bottle()


@app.route('/static/<filename>', method='GET', name='static')
def static(filename):
    return static_file(filename, root='./static/')


@app.route('/', method='GET', name='index')
@view('templates/index.html')
def index():
    response = {}
    return response



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888, reloader=True, debug=True)
