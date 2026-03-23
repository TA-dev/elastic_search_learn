from config import *
from utils import *
from index_data import *
import math
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from  fastapi.responses import HTMLResponse
from typing import Optional
from sentence_transformers import SentenceTransformer

app = FastAPI()
es = get_elasticsearch_client(max_try=3, sleep_time=0) # to prevent pausing the program

app.add_middleware(  # allows frontend to access backend
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# device = 'cuda' if torch.cuda.is_available() else 'cpu'
# print(f"Using device: {device}")
# model = SentenceTransformer('all-MiniLM-L6-v2').to(device)

# ------------------------
# GLOBAL STATE
# ------------------------
current_tokenizer: Optional[str] = None  # remembers last used tokenizer
# ------------------------
# HELPER FUNCTIONS
# ------------------------
def get_total_hits(response):
    return response["hits"]["total"]["value"]

def calculate_max_pages(total_hits, limit):
    return math.ceil(total_hits / limit)

# ------------------------
# SEARCH ENDPOINT
# ------------------------
@app.get("/api/v1/regular_search")
async def search(
    search_query: str,
    skip: int = 0,
    limit: int = 10,
    year: Optional[str] = None,
    tokenizer: Optional[str] = None   # comes from frontend
) -> dict:
    global INDEX_NAME_N_GRAM, INDEX_NAME_DEFAULT
    global INDEX_NAME_RAW_DEFAULT, INDEX_NAME_RAW_N_GRAM
    global use_raw
    global current_tokenizer

    # ------------------------
    # UPDATE TOKENIZER STATE
    # ------------------------
    if tokenizer:
        current_tokenizer = tokenizer  # remember last choice
    print("using tokenizer:", current_tokenizer)

    # ------------------------
    # SELECT INDEX
    # ------------------------
    if current_tokenizer == "N-Gram":
        index_name = INDEX_NAME_RAW_N_GRAM if use_raw else INDEX_NAME_N_GRAM
    else:
        index_name = INDEX_NAME_RAW_DEFAULT if use_raw else INDEX_NAME_DEFAULT
    print("using index:", index_name)
    # ------------------------
    # BUILD QUERY
    # ------------------------
    query = {
        "bool": {
            "must": [
                {
                    "multi_match": {
                        "query": search_query,
                        "fields": ["title", "explanation"]
                    }
                }
            ]
        }
    }

    # ------------------------
    # YEAR FILTER
    # ------------------------
    if year:
        query["bool"]["filter"] = {
            "range": {
                "date": {
                    "gte": f"{year}-01-01",
                    "lte": f"{year}-12-31",
                    "format": "yyyy-MM-dd"
                }
            }
        }

    # ------------------------
    # SEARCH
    # ------------------------
    response = es.search(
        index=index_name,
        body={
            "query": query,
            "from": skip,
            "size": limit
        },
        filter_path=["hits.hits._source", "hits.hits._score", "hits.total"]
    )

    # ------------------------
    # RESULTS PROCESSING
    # ------------------------
    total_hits = get_total_hits(response)
    max_pages = calculate_max_pages(total_hits, limit)
    hits = response["hits"].get("hits", [])

    return {
        "hits": hits,
        "total": total_hits,
        "max_pages": max_pages
    }





# defining semantic search endpoint
@app.get("/api/v1/semantic_search")
async def semantic_search(search_query: str, skip: int = 0, limit: int = 10, year: str | None = None) -> dict:
    global INDEX_NAME_EMBEDDINGS, INDEX_NAME_RAW_EMBEDDINGS, model
    embedded_query = model.encode(search_query)
    query = {
        "bool" : {
            "must": [
                {
                    "knn": {
                        "field": "embedding",
                        "query_vector": embedded_query,
                        "k": 1e4  # # higher than total docs (3333), so effectively retrieve all possible matches (within ES limits)
                    }
                }
            ]
        }
    }
    if year:
        query["bool"]["filter"] = {
            "range": {
                "date": {
                    "gte": f"{year}-01-01",
                    "lte": f"{year}-12-31" ,
                    "format": "yyyy-MM-dd"
                }
            }
        }

    response = es.search(
    index=INDEX_NAME_EMBEDDINGS if not use_raw else INDEX_NAME_RAW_EMBEDDINGS, 
    body={
        "query": query,
        "from": skip,
        "size": limit

    },
    filter_path=["hits.hits._source", "hits.hits._score", "hits.total"]
)
        

    total_hits = get_total_hits(response)
    max_pages = calculate_max_pages(total_hits, limit)

    hits = response["hits"].get("hits", [])  # in case nothing matches the search, so we dont get errors
    return {"hits": hits, "total": total_hits, "max_pages": max_pages}

    

# aggregations for how many docs per year
@app.get("/api/v1/get_docs_per_year_count")
async def get_docs_per_year_count(search_query: str) -> dict:
    global INDEX_NAME
    try:

        query = {
            "bool" : {
                "must": [
                    {
                        "multi_match": {
                            "query": search_query,
                            "fields": ["title", "explanation"]
                        }
                    }
                ]
            }
        }

        response = es.search(
            index=INDEX_NAME, 
            body={
                "query": query,
                "aggs": {
                    
                    "docs_per_year": {
                        "date_histogram": {
                            "field": "date",
                            "calendar_interval": "year",  # group by year
                            "format": "yyyy" # format the year in response
                        }
                    }
                }     
            },
            filter_path=["aggregations.docs_per_year"]
            
        )
        return {"docs_per_year": extract_docs_per_year(response)}

    except Exception as e:
        print(e)
        return HTMLResponse(content=str(e), status_code=500)


def extract_docs_per_year(response):
    docs_per_year = {}
    for bucket in response["aggregations"]["docs_per_year"]["buckets"]:
        docs_per_year[bucket["key_as_string"]] = bucket["doc_count"]
    return docs_per_year