import json

from bottle import Bottle, HTTPError, request, template, route, static_file, view, redirect
from pymongo import MongoClient

from config import SERVER_HOST, SERVER_PORT, MONGO_HOST, MONGO_PORT, MONGO_DB

# app and routers
app = Bottle()

# mongo client
client = MongoClient(MONGO_HOST, MONGO_PORT)
db = client[MONGO_DB]

@app.route('/static/<filename:path>', method='GET', name='static')
def static(filename):
    return static_file(filename, root='./static/')


@app.route('/', method='GET', name='index')
@view('templates/index.html')
def index():
    experiments_collection = db['default.runs']

    experiments_info = extract_info(experiments_collection)

    response = {
        'experiments_info': experiments_info
    }

    return response


def extract_info(experiments_collection):
    experiments = experiments_collection.find({"status": "COMPLETED"})

    result = [
        {
            'model': e['config']['model_class'].replace('Physionet', '').replace('Model', ''),
            'start_time': e['start_time'],
            'stop_time': e['stop_time'],
            'result': e['result']
        }
        for e in experiments
    ]


    return result


if __name__ == '__main__':
    app.run(host=SERVER_HOST, port=SERVER_PORT, reloader=True, debug=True)
