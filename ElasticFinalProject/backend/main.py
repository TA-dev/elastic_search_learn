from config import *
from utils import *
from index_data import *

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(  # allows frontend to access backend
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# defining endpoint

@app.get("/api/v1/search/")
async def search(search_query: str, skip: int = 0, limit: int = 10) -> dict:
    # a simple search query
    es = get_elasticsearch_client()
    response = es.search(
        index=INDEX_NAME, 
        body={
            "query": {
                "multi_match": {
                    "query": search_query,
                    "fields": ["title", "explanation"]
                }
            },
            "from": skip,
            "size": limit
        }, 
        filter_path=["hits.hits._source", "hits.hits._score"]
    )
    hits = response["hits"]["hits"]
    return {"hits": hits}

        
   