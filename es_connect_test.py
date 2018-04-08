#coding=utf8

import os
from os import walk

import time
from datetime import datetime
import json
import csvop

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk



class ElasticObj:
    def __init__(self, ip ="127.0.0.1"):
        '''
        :param index_name: 索引名称
        :param index_type: 索引类型
        '''
        # 无用户名密码状态
        self.es = Elasticsearch([ip])
        #用户名密码状态
        #self.es = Elasticsearch([ip],http_auth=('elastic', 'password'),port=9200)


    def check(self):
        '''
        输出当前系统的ES信息
        :return:
        '''
        return self.es.info()



    def create_index(self, index_name, index_mappings):
        '''
        创建索引,创建索引名称为index_name，类型为index_type的索引
        :param index_mappings: 创建索引的映射
        :return:
        '''
        if self.es.indices.exists(index=index_name) is not True:
            _created = self.es.indices.create(index=index_name, body=index_mappings)
            print(_created)
            return _created


    def insert_one_document(self, index_name, index_type, body, id=None):
        '''
        插入一条数据body到指定的index、指定的type下;可指定Id,若不指定,ES会自动生成
        :param index_name: 待插入的index值
        :param index_type: 待插入的type值
        :param body: 待插入的数据 -> dict型
        :param id: 自定义Id值
        :return:
        '''
        _inserted = self.es.index(index=index_name, doc_type=index_type, body=body, id=id)
        print(_inserted['result'])
        return _inserted


    def index_data_fromCSV(self, index_name, index_type, csvfile):
        '''
        从CSV文件中读取数据，并存储到es中
        :param csvfile: csv文件，包括完整路径
        :return:
        '''
        data_list = csvop.read_csv(csvfile)
        index = 0
        doc = {}
        title = []
        title_num = len(data_list[0])
        for i in range(title_num):#第一行是标题
            title.append(data_list[0][i])
        for item in data_list:
            if index >= 1:
                for i in range(title_num):
                    doc[title[i]] = item[i]
                res = self.es.index(index=index_name, doc_type=index_type, body=doc)
                print(res['result'])
            index += 1
            #print(index)

    def insert_DataFrame(self, index_name, index_type, dataFrame):
        '''
        使用bulk方法批量插入接口;
        bulk接口所要求的数据列表结构为:[{{optionType}: {Condition}}, {data}]
        其中optionType可为index、delete、update
        Condition可设置每条数据所对应的index值和type值
        data为具体要插入/更新的单条数据
        :param index_name: 默认插入的index值
        :param index_type: 默认插入的type值
        :param dataFrame: 待插入数据集
        :return:
        '''
        index_name = index_name
        index_type = index_type
        dataList = dataFrame.to_dict(orient='records')
        insertHeadInfoList = [{"index": {}} for i in range(len(dataList))]
        temp = [dict] * (len(dataList) * 2)
        temp[::2] = insertHeadInfoList
        temp[1::2] = dataList
        try:
            return self.es.bulk(index=index_name, doc_type=index_type, body=temp)
        except Exception, e:
            return str(e)


    def deleteDocById(self, index_name, index_type, id):
        '''
        删除指定index、type、id对应的数据
        :param index_name:
        :param index_type:
        :param id:
        :return:
        '''
        return self.es.delete(index=index_name, doc_type=index_type, id=id)

    def deleteDocByQuery(self, index_name, query, doc_type=None):
        '''
        删除idnex下符合条件query的所有数据
        :param index_name:
        :param query: 满足DSL语法格式
        :param doc_type:
        :return:
        '''
        try:
            res = self.es.delete_by_query(index=index_name, body=query, doc_type=doc_type)
            return res
        except Exception, e:
            return str(e)

    def searchDoc(self, index_name=None, doc_type=None, body=None):
        '''
        查找index下所有符合条件的数据
        :param index_name:
        :param doc_type:
        :param body: 筛选语句,符合DSL语法格式
        :return:
        '''
        _searched = self.es.search(index=index_name, doc_type=doc_type, body=body)
        #for hit in _searched['hits']['hits']:
            # print hit['_source']
        return _searched

    def getDocById(self, index_name, doc_type, id):
        '''
        获取指定index_name、doc_type、id对应的数据
        :param index_name:
        :param doc_type:
        :param id:
        :return:
        '''
        _searched = self.es.get(index=index_name, doc_type=doc_type, id=id)
        #for hit in _searched['hits']['hits']:
            # print hit['_source']
        return _searched


    def updateDocById(self, index_name, doc_type, id, body=None):
        '''
        更新指定index_name、doc_type、id对应的数据
        :param index_name:
        :param doc_type:
        :param id:
        :param body: 待更新的值
        :return:
        '''
        _updated = self.es.update(index=index_name, doc_type=doc_type, id=id, body=body)
        return _updated



