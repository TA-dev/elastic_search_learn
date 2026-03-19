from config import *
from utils import *
from index_data import *
import math
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from  fastapi.responses import HTMLResponse

app = FastAPI()
es = get_elasticsearch_client(max_try=3, sleep_time=0) # to prevent pausing the program

app.add_middleware(  # allows frontend to access backend
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# defining endpoint

@app.get("/api/v1/regular_search")
async def search(search_query: str, skip: int = 0, limit: int = 10, year: str | None = None) -> dict:
    # a simple search query
    
    # compound query so we can add filters
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
        index=INDEX_NAME, 
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

def get_total_hits(response):
    return response["hits"]["total"]["value"]

def calculate_max_pages(total_hits, limit):
    return math.ceil(total_hits / limit)


# aggregations for how many docs per year
@app.get("/api/v1/get_docs_per_year_count")
async def get_docs_per_year_count(search_query: str) -> dict:
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

   