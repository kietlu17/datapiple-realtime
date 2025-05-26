# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


import scrapy
import json
# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
import csv
import pymongo
from kafka import KafkaProducer

class JsonDBBookPipeline:
    def process_item(self, item, spider):
        with open('jsondataunitop.json', 'a', encoding='utf-8') as file:
            line = json.dumps(dict(item), ensure_ascii=False) + '\n'
            file.write(line)
        return item

class CSVDBBookPipeline:
    '''
    mỗi thông tin cách nhau với dấu $
    Ví dụ: coursename$lecturer$intro$describe$courseUrl
    Sau đó, cài đặt cấu hình để ưu tiên Pipline này đầu tiên
    '''
    def process_item(self, item, spider):
        with open('csvdataunitop.csv', 'a', encoding='utf-8', newline='') as file:
            writer = csv.writer(file, delimiter='$')
            writer.writerow([
                item['bookUrl'],
                item['number'],
                item['bookname'],
                item['author'],
                item['prices'],
                item['describe'],
                item['rating'],
                item['ratingcount'],
                item['reviews'],
                item['fivestars'],
                item['fourstars'],
                item['threestars'],
                item['twostars'],
                item['onestar'],
                item['pages'],
                item['publish'],
                item['authorUrl'],
                item['genre'],
                item['score'],
                item['votes']
            ])
        return item 
    pass

class MongoDBUnitopPipeline:
    def __init__(self):
        # Connection String
        
        #self.client = pymongo.MongoClient('mongodb://mymongodb:27017')
        self.client = pymongo.MongoClient('mongodb://mongodb:27017')
        self.db = self.client['db_goodread'] #Create Database      

        pass
    
    def process_item(self, item, spider):
        
        collection =self.db['tb_book'] #Create Collection or Table
        try:
            collection.insert_one(dict(item))
            return item
        except Exception as e:
            raise DropItem(f"Error inserting item: {e}")       
        pass

class KafkaPipeline:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers='kafka:29092',
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        self.topic = 'goodread'
    
    def process_item(self, item, spider):
    #     self.producer.send(self.topic, json.dumps(dict(item)).encode('utf-8'))
    #     return item
    # pass
        try:
            self.producer.send(self.topic, value=dict(item))
            self.producer.flush()
            return item
        except Exception as e:
            raise DropItem(f"Error inserting item: {e}")
