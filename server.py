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
    experiments = list(experiments_collection.find({"status": "COMPLETED"}))

    experiments_info = extract_info(experiments)
    config_values = extract_config_values(experiments)

    response = {
        'experiments_info': experiments_info,
        'config_values': config_values,
    }

    return response

def extract_config_values(experiments):
    result = set([c for e in experiments for c in e['config'].keys()])
    result ^= {'seed', 'model_class'}
    result = sorted(result)

    return result


def extract_info(experiments):
    result = [
        {
            'model': e['config']['model_class'].replace('Physionet', '').replace('Model', ''),
            'start_time': e['start_time'],
            'stop_time': e['stop_time'],
            'result': e['result'],
            'config': e['config'],
        }
        for e in experiments
    ]


    return result


if __name__ == '__main__':
    app.run(host=SERVER_HOST, port=SERVER_PORT, reloader=True, debug=True)
