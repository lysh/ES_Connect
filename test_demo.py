#coding=utf-8

import csv
import csvop
from es_connect_test import ElasticObj
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

es =ElasticObj()

#print(es.check())

# doc_mappings = {"mappings" : {
#     "type1" : {
#         "properties" : {
#             "field1" : { "type" : "text" }
#         }
#     }
# }}
# es.create_index('nametest', doc_mappings)

#es.insert_one_document("ott", "ott_type", {"S6406527": "9264","S0068565": "20464","S0068690": "10412","DATETIME": "2019-01-31"})



#es.index_data_fromCSV('testname', 'testtype', 'HYL_AH_Data.csv')


# _index = 'demo'
# _type = 'test_df'
# import pandas as pd
# frame = pd.DataFrame({'name': ['tomaaa', 'tombbb', 'tomccc'],
#                       'sex': ['male', 'famale', 'famale'],
#                       'age': [3, 6, 9],
#                       'address': [u'合肥', u'芜湖', u'安徽']})
# print(frame)

# print(es.insert_DataFrame(_index, _type, frame))


# host = 'localhost:9200'
# _index = 'demo'
# _type = 'test_df'
# #批量插入接口
# doc = [
#     {"index": {}},
#     {'name': 'jackaaa', 'age': 2000, 'sex': 'female', 'address': u'西安'},
#     {"index": {}},
#     {'name': 'jackbbb', 'age': 3000, 'sex': 'male', 'address': u'合肥'},
#     {"index": {}},
#     {'name': 'jackccc', 'age': 4000, 'sex': 'female', 'address': u'安徽'},
#     {"index": {}},
#     {'name': 'jackddd', 'age': 1000, 'sex': 'male', 'address': u'阜阳'},
#     ]
# print(Elasticsearch([host]).bulk(index=_index, doc_type=_type, body=doc))



#Search API
#query = {'query': {'match_all': {}}}
#print es.searchDoc('demo', 'test_df', query)['hits']['hits'][0]
# query = {'query': {'term': {'name': 'jackaaa'}}}
# print es.searchDoc('demo', 'test_df', query)
# query = {'query': {'range': {'age': {'gt': 11}}}}
# query = {'query': {'range': {'age': {'lt': 11}}}}
# query = {'query': {'match': {'age': 1000}}}
# print es.searchDoc('demo', 'test_df', query)
# print(es.searchDoc())

# Get API
# print es.getDocById('demo', 'test_df', 'aDXsoGIBo1UAretD2N4p')


# Update API
# body = {'script': "ctx._source.remove('age')"}#删除字段
# body = {'script': "ctx._source.age = 40"}#增加字段
# body = {"doc": {"name": 'jackaaa'}}#修改部分字段
# print es.updateDocById('demo', 'test_df', 'aDXsoGIBo1UAretD2N4p', body)


# Delete API
# body = {"query": {"name": 'jackbbb', 'sex': 'male'}}
# print es.deleteDocById('demo', 'test_df', 'aDXsoGIBo1UAretD2N4p')

# Delete_By_Query API
# query = {'query': {'match': {'sex': 'male'}}}
# query = {'query': {'range': {'age': {'lt': 11}}}}
# print es.deleteDocByQuery('demo', query, 'test_df')
# print(es.deleteDocByQuery('demo', {'query': {'match_all': {}}}))
