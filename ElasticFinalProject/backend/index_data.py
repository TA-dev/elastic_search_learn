# reads apod.json and indexes the documents inside it in elastic search
import json
from elasticsearch import Elasticsearch
from elasticsearch import helpers
from pprint import pprint
import base64
from typing import List
from utils import *
from config import *
from tqdm import tqdm


def index_data(documents: List[dict]):
    # indexes the documents in elastic search using bulk api
    es = get_elasticsearch_client(max_try=5)
    if es is None:
        return
    _ = _create_index(es)
    _ = _insert_documents(es, documents)

    pprint(f"Indexed {len(documents)} documents into Elasticsearch index {INDEX_NAME}")
   
def _create_index(es: Elasticsearch) -> Elasticsearch:
    es.indices.delete(index=INDEX_NAME, ignore_unavailable=True)
    return es.indices.create(index=INDEX_NAME)

def _insert_documents(es: Elasticsearch, documents: List[dict]) -> dict:
    actions = []
    for doc in tqdm(documents, total=len(documents)):
        actions.append({
            "_index": "apod",
            "_source": doc
        })
    return helpers.bulk(es, actions)

if __name__ == "__main__":
    with open("../../data/apod.json") as f:
        documents = json.load(f)
    index_data(documents=documents)
     

