SERVER_HOST = '0.0.0.0'
SERVER_PORT = 8080

MONGO_HOST = '127.0.0.1'
MONGO_PORT = 27018

# define the order of results, label, key, and default visibility
#
# a list of tuples ('db_name - str', 'interface_name - str', 'show by default - boolean'),
# an example:
# ('score_train', 'Train Score', True),
RESULTS_NAMES = []

# define a list of filters
# each filter has the following structure
#     {
#         'name': 'Filter name',
#         'key': 'fieldname in the database',
#         'values': [
#             ('Display name 1', 'Value 1 of the key'),
#             ('Display name 2', 'Value 2 of the key'),
#             ('All', '',),
#         ],
#     },
#
# an example:
# filters = [
#     {
#         'name': 'Model',
#         'key': 'config.model_class',
#         'values': [
#             ('Timeseries', 'PhysionetTimeseriesModel'),
#             ('GRU-D', 'PhysionetTimeseriesGRUDModel',),
#             ('AdaptiveRNN', 'PhysionetTimeseriesAdaptiveRNNModel',),
#             ('AdaptiveTwoRNN', 'PhysionetTimeseriesAdaptiveTwoRNNModel',),
#             ('Features', 'PhysionetFeaturesModel',),
#             ('All', '',),
#         ],
#     },
# ]
FILTERS = []


from config_local import *
