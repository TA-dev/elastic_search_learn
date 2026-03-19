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

use_n_gram_tokenizer = True
INDEX_NAME = INDEX_NAME_N_GRAM if use_n_gram_tokenizer else INDEX_NAME_DEFAULT
print(INDEX_NAME)
tokenizer_name = 'standard' if not use_n_gram_tokenizer else 'n_gram_tokenizer'




def index_data(documents: List[dict]):
    global INDEX_NAME, use_n_gram_tokenizer
    # indexes the documents in elastic search using bulk api
    es = get_elasticsearch_client(max_try=5)
    if es is None:
        return
    _ = _create_index(es)
    _ = _insert_documents(es, documents)

    pprint(f"Indexed {len(documents)} documents into Elasticsearch index {INDEX_NAME}")
   
def _create_index(es: Elasticsearch) -> Elasticsearch:    
    global INDEX_NAME, tokenizer_name, use_n_gram_tokenizer
    
    tokenizer = {
        "n_gram_tokenizer": {
            "type": "ngram",
            "min_gram": 1,
            "max_gram": 30,
            "token_chars": ["letter", "digit", "punctuation", "symbol"]
        }
    }

    es.indices.delete(index=INDEX_NAME, ignore_unavailable=True)

    return es.indices.create(index=INDEX_NAME, body={
        "settings": {
           
            "index": {
                "max_ngram_diff": 50
            },
            "analysis": {
                "analyzer": {
                    "default": {
                        "type": "custom",
                        "tokenizer": tokenizer_name
                    }
                },
                "tokenizer": tokenizer
            }
        }
    })

def _insert_documents(es: Elasticsearch, documents: List[dict]) -> dict:
    global INDEX_NAME
    actions = []
    for doc in tqdm(documents, total=len(documents)):
        actions.append({
            "_index": INDEX_NAME,
            "_source": doc
        })
    return helpers.bulk(es, actions)

if __name__ == "__main__":
    with open("./data/apod.json") as f:
        documents = json.load(f)
    index_data(documents=documents)
     

