from sentence_transformers import SentenceTransformer
import torch


# defining constants

INDEX_NAME_DEFAULT = "apod"
INDEX_NAME_N_GRAM = "apod_n_gram"
INDEX_NAME_EMBEDDINGS = "apod_embedding"
INDEX_NAME_RAW_EMBEDDINGS = "apod_raw_embedding"
INDEX_NAME_RAW_N_GRAM = "apod_raw_n_gram"
INDEX_NAME_RAW_DEFAULT = "apod_raw"


# here either ngram is true OR embeddings
use_n_gram_tokenizer = True
use_embeddings = False

# can be true with one of the previous flags true as well
use_raw = True


# if using n-gram tokenizer, change the index name to INDEX_NAME_N_GRAM, if using embeddings, 
# change the index name to INDEX_NAME_EMBEDDINGS, if raw (with either n-gram or embeddings), change the index name to INDEX_NAME_RAW, else use INDEX_NAME_DEFAULT
if use_n_gram_tokenizer and use_embeddings and use_raw:
    INDEX_NAME = INDEX_NAME_RAW_EMBEDDINGS
elif use_n_gram_tokenizer and use_embeddings:
    INDEX_NAME = INDEX_NAME_EMBEDDINGS
elif use_n_gram_tokenizer and use_raw:
    INDEX_NAME = INDEX_NAME_RAW_N_GRAM
elif use_embeddings and use_raw:
    INDEX_NAME = INDEX_NAME_RAW_EMBEDDINGS
elif use_n_gram_tokenizer:
    INDEX_NAME = INDEX_NAME_N_GRAM
elif use_embeddings:
    INDEX_NAME = INDEX_NAME_EMBEDDINGS
elif use_raw:
    INDEX_NAME = INDEX_NAME_RAW_DEFAULT
else:
    INDEX_NAME = INDEX_NAME_DEFAULT

print(f"Using index: {INDEX_NAME}")

# either standard or ngram. if embedding, we dont use tokenizer
if use_embeddings:
    tokenizer_name = None
else:
    tokenizer_name = 'standard' if not use_n_gram_tokenizer else 'n_gram_tokenizer'


# if using embedding, we initialize the sentence transformer model, otherwise we use no model
# if use_embeddings:
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"Using device: {device}")
model = SentenceTransformer('all-MiniLM-L6-v2').to(device)
# else:
#     model = None