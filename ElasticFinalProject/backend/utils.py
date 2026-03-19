from elasticsearch import Elasticsearch
import time
from pprint import pprint

def get_elasticsearch_client(max_try=2, sleep_time=0) -> Elasticsearch:
    """
    Tries to initialize an Elasticsearch client up to max_try times.
    Returns Elasticsearch client if successful, None otherwise.
    """
    attempt = 0
    while attempt < max_try:
        try:
            es = Elasticsearch("http://localhost:9200")
            
            # Check connection
            if es.ping():
                print("Elasticsearch client initialized successfully")
                # info = es.info()
                # pprint(f"Cluster info:\n {info}")
                return es
            else:
                print(f"Ping failed on attempt {attempt+1}/{max_try}")
        except Exception as e:
            print(f"Failed to connect on attempt {attempt+1}/{max_try}: {e}")
        
        attempt += 1
        print(f"Retrying in {sleep_time} seconds...")
        time.sleep(sleep_time)
    
    print("Could not initialize Elasticsearch client after max attempts")
    return None