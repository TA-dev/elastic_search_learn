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
    global INDEX_NAME, use_n_gram_tokenizer
    # indexes the documents in elastic search using bulk api
    es = get_elasticsearch_client(max_try=5)
    if es is None:
        return
    _ = _create_index(es)
    _ = _insert_documents(es, documents)

    pprint(f"Indexed {len(documents)} documents into Elasticsearch index {INDEX_NAME}")

def _create_index(es: Elasticsearch) -> Elasticsearch:
    if use_embeddings:
        return _create_index_embeddings(es)
    else:
        return _create_index_no_embedding(es)


# function to create index (no embeddings)
def _create_index_no_embedding(es: Elasticsearch) -> Elasticsearch:    
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

def _create_index_embeddings(es: Elasticsearch) -> Elasticsearch:
    global INDEX_NAME, tokenizer_name, use_n_gram_tokenizer
    es.indices.delete(index=INDEX_NAME, ignore_unavailable=True)

    return es.indices.create(index=INDEX_NAME, mappings={  # manual mapping bc elasticsearch can't infer dense vectors automatically
        "properties": {
            "embedding": {
                "type": "dense_vector",
            }  
        }
    })

def _insert_documents(es: Elasticsearch, documents: List[dict]) -> dict:
    global INDEX_NAME, model
    actions = []
    for doc in tqdm(documents, total=len(documents)):
        # if we use embedding, add embedding field
        if use_embeddings:
            doc['embedding'] = model.encode(doc['explanation'])
        actions.append({
            "_index": INDEX_NAME,
            "_source": doc
        })
    return helpers.bulk(es, actions)

if __name__ == "__main__":
    with open("./data/apod.json") as f:
        documents = json.load(f)
    index_data(documents=documents)
     

