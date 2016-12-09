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
    filters = get_filters()

    experiments, current_filters = find_experiments(db, request.query, filters)

    experiments_info = extract_info(experiments)
    config_values = extract_config_values(experiments)
    results = get_results_names()

    response = {
        'experiments_info': experiments_info,

        'config_values': config_values,

        'results': results,

        'filters': filters,
        'current_filters': current_filters,
        'format_url': format_url,
    }

    return response


def format_url(current_filters, key, value):
    new_filters = current_filters.copy()
    new_filters[key] = value
    if value == '':
        new_filters.pop(key)

    url_params = '&'.join([fk + '=' + fv for fk, fv in new_filters.items()])

    return '/?' + url_params

def find_experiments(db, query, filters):
    db_query = {"status": "COMPLETED"}
    current_filters = {}

    for f in filters:
        key = f['key']
        if key in query:
            val = query[key]

            if val == '':
                continue

            current_filters[key] = val

            if val in ('true', 'false'):
                val = True if val == 'true' else False

            db_query[key] = val

    experiments_collection = db['default.runs']
    experiments = list(experiments_collection.find(db_query))

    return experiments, current_filters


def get_filters():
    filters = [
        {
            'name': 'Model',
            'key': 'config.model_class',
            'values': [
                ('Timeseries', 'PhysionetTimeseriesModel'),
                ('Features', 'PhysionetFeaturesModel',),
                ('All', '',),
            ],
        },
        {
            'name': 'Masking',
            'key': 'config.append_missing',
            'values': [
                ('Yes', 'true'),
                ('No', 'false',),
                ('All', '',),
            ],
        },
    ]

    return filters


def get_results_names():
    # define the order of results, label, key, and default visibility
    results = [
        ('score_train', 'Train Score', True),
        ('precision_train', 'Train Precision', False),
        ('recall_train', 'Train Recall', False),
        ('auc_train', 'Train AUC', True),

        ('score_val', 'Val Score', True),
        ('precision_val', 'Val Precision', False),
        ('recall_val', 'Val Recall', False),
        ('auc_val', 'Val AUC', True),
    ]

    return results


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
