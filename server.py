import json
import copy

from bottle import Bottle, HTTPError, request, template, route, static_file, view, redirect
import pymongo
from pymongo import MongoClient

from config import SERVER_HOST, SERVER_PORT, MONGO_HOST, MONGO_PORT

# app and routers
app = Bottle()

# mongo client
client = MongoClient(MONGO_HOST, MONGO_PORT)


@app.route('/static/<filename:path>', method='GET', name='static')
def static(filename):
    return static_file(filename, root='./static/')


@app.route('/', method='GET', name='home')
@view('templates/home.html')
def index():
    databases = client.database_names()

    databases_with_urls = [(db, app.get_url('experiments', db_name=db)) for db in databases]

    response = {
        'databases': databases_with_urls,
    }

    return response


@app.route('/experiments/<db_name>/', method='GET', name='experiments')
@view('templates/experiments.html')
def index(db_name):
    filters = get_filters()

    db = client[db_name]

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
        'format_config_values': format_config_values,
    }

    return response


def format_url(current_filters, key, value):
    new_filters = copy.deepcopy(current_filters)

    if not key in new_filters:
        new_filters[key] = []

    if value != '':
        if value not in new_filters[key]:
            new_filters[key].append(value)
        else:
            new_filters[key].remove(value)
    else:
        new_filters.pop(key)

    params = [fk + '=' + fv for fk, fvals in new_filters.items() for fv in fvals]

    return '' + ('?' + '&'.join(params) if len(params) > 0 else '')


def find_experiments(db, query, filters):
    current_filters = {}

    for f in filters:
        key = f['key']
        if key in query:
            vals = query.getall(key)

            current_filters[key] = vals

    db_query = build_db_query(current_filters)

    experiments_collection = db['default.runs']
    experiments = list(experiments_collection.find(
        db_query
        # , sort=[("result.auc_val", pymongo.DESCENDING)], limit=1000
    ))

    return experiments, current_filters


def build_db_query(current_filters):
    def transoform_val(v):
        if v == 'true':
            return True
        if v == 'false':
            return False
        return v

    filters = {key: [transoform_val(v) for v in vals] for key, vals in current_filters.items()}

    db_query = {"status": "COMPLETED"}
    for key, vals in filters.items():
        if len(vals) == 1:
            db_query[key] = vals[0]
        else:
            db_query['$or'] = [{key: v} for v in vals]

    return db_query


def get_filters():
    filters = [
        {
            'name': 'Model',
            'key': 'config.model_class',
            'values': [
                ('Timeseries', 'PhysionetTimeseriesModel'),
                ('GRU-D', 'PhysionetTimeseriesGRUDModel',),
                ('AdaptiveRNN', 'PhysionetTimeseriesAdaptiveRNNModel',),
                ('AdaptiveTwoRNN', 'PhysionetTimeseriesAdaptiveTwoRNNModel',),
                ('Features', 'PhysionetFeaturesModel',),
                ('All', '',),
            ],
        },
        {
            'name': 'Data type',
            'key': 'config.data_type',
            'values': [
                ('Sampled', 'sampled'),
                ('Unsampled', 'unsampled',),
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
        {
            'name': 'Delta',
            'key': 'config.append_delta',
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


def format_config_values(val):
    if isinstance(val, float):
        if abs(val) >= 0.001:
            return '{:.3f}'.format(val)
        else:
            return '{:.2e}'.format(val)

    return val


if __name__ == '__main__':
    app.run(host=SERVER_HOST, port=SERVER_PORT, reloader=True, debug=True)
