from elasticsearch import Elasticsearch
import time
import pprint

def get_elasticsearch_client(max_try=2, sleep_time=1) -> Elasticsearch:
    # Try and initialize the Elasticsearch client without erros max_try times
    try:
        if max_try >=0:
            es = Elasticsearch('http://localhost:9200')
            # check if connected succesfully
            info = es.info()
            print("Elasticsearch client initialized successfully")
            pprint(f"Cluster info:\n {info}") # print cluster info
            return es
        else:
            return None
    except:
        if max_try > 0:
            max_try -= 1
            print("Failed to initialize elasticsearch client. Retrying...")
            time.sleep(sleep_time) # to not overload the server
            return get_elasticsearch_client(max_try, sleep_time)
        else:
            return None
    