from sentence_transformers import SentenceTransformer
import torch


# defining constants

INDEX_NAME_DEFAULT = "apod"
INDEX_NAME_N_GRAM = "apod_n_gram"
INDEX_NAME_EMBEDDINGS = "apod_embedding"


use_n_gram_tokenizer = False
use_embeddings = True
# if using n-gram tokenizer, change the index name to INDEX_NAME_N_GRAM, if using embeddings, change the index name to INDEX_NAME_EMBEDDINGS, else use INDEX_NAME_DEFAULT
if use_n_gram_tokenizer:
    INDEX_NAME = INDEX_NAME_N_GRAM
elif use_embeddings:
    INDEX_NAME = INDEX_NAME_EMBEDDINGS
else:
    INDEX_NAME = INDEX_NAME_DEFAULT
print(INDEX_NAME)

# either standard or ngram. if embedding, we dont use tokenizer
if use_embeddings:
    tokenizer_name = None
else:
    tokenizer_name = 'standard' if not use_n_gram_tokenizer else 'n_gram_tokenizer'


# if using embedding, we initialize the sentence transformer model, otherwise we use no model
if use_embeddings:
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Using device: {device}")
    model = SentenceTransformer('all-MiniLM-L6-v2').to(device)
else:
    model = None