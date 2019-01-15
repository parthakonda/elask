"""
Frequently used elasticsearch functions
"""
from elasticsearch import Elasticsearch, helpers
from elasticsearch_dsl import Q, Search
from server import app


class ESManager(object):

    def __init__(self):
        self.client = Elasticsearch(app.config['ELASTICSEARCH_DOMAIN'])

    def get_indices(self):
        """ To return the list of indices available """
        all_indcies = list(self.client.indices.get_alias().keys())
        if '.kibana' in all_indcies:
            all_indcies.remove('.kibana')
        return all_indcies

    def delete_all_indexes(self):
        """ To delete all the indexes """
        for every_index in self.get_indices():
            self.client.indices.delete(index=every_index, ignore=[400, 404])
        return True
