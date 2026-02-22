# services/rag_service.py
import os
import json
import torch
import lancedb
import pyarrow as pa
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForCausalLM

from config import EMBEDDING_MODEL_PATH, LANCEDB_DIR, ALLOWED_TABLES, RERANK_MODEL_PATH

print("Initializing Embedding model. This may take a moment...")
embedding_model = SentenceTransformer(EMBEDDING_MODEL_PATH)
print("Embedding Model loaded successfully.")

EMBEDDING_DIM = embedding_model.get_sentence_embedding_dimension()

print("Initializing Qwen CausalLM Reranker model. This may take a moment...")
rerank_tokenizer = AutoTokenizer.from_pretrained(
    RERANK_MODEL_PATH,
    padding_side="left",
    trust_remote_code=True
)
rerank_model = AutoModelForCausalLM.from_pretrained(
    RERANK_MODEL_PATH,
    torch_dtype=torch.bfloat16,
    attn_implementation="flash_attention_2",
    device_map="auto",
    trust_remote_code=True
).eval()

yes_id = rerank_tokenizer.convert_tokens_to_ids("yes")
no_id = rerank_tokenizer.convert_tokens_to_ids("no")

print("Qwen Reranker Model loaded successfully.")

print("Initializing LanceDB and creating partitioned tables...")
os.makedirs(LANCEDB_DIR, exist_ok=True)
db = lancedb.connect(LANCEDB_DIR)

schema = pa.schema([
    pa.field("vector", pa.list_(pa.float32(), EMBEDDING_DIM)),
    pa.field("data", pa.string())
])

tables = {}
for table_name in ALLOWED_TABLES:
    tables[table_name] = db.create_table(table_name, schema=schema, exist_ok=True)
print(f"LanceDB initialized. 4 partitioned tables are ready.")


def validate_table_name(table_name: str):
    if table_name not in ALLOWED_TABLES:
        raise ValueError(f"Invalid table name '{table_name}'. Must be one of {ALLOWED_TABLES}")


def text_to_embedding_str(text: str) -> str:
    try:
        vector = embedding_model.encode(text).tolist()
        return json.dumps(vector)
    except Exception as e:
        raise Exception(f"Embedding generation failed: {str(e)}")


def insert_to_db(vector_str: str, data_str: str, table_name: str) -> None:
    validate_table_name(table_name)
    try:
        vector = json.loads(vector_str)
        if len(vector) != EMBEDDING_DIM:
            raise ValueError(f"Vector dimension mismatch. Expected {EMBEDDING_DIM}, got {len(vector)}")
        
        tables[table_name].add([{"vector": vector, "data": data_str}])
    except Exception as e:
        raise Exception(f"Database insertion failed: {str(e)}")


def delete_by_data(data_str: str, table_name: str) -> None:
    validate_table_name(table_name)
    try:
        safe_data_str = data_str.replace("'", "''")
        tables[table_name].delete(where=f"data = '{safe_data_str}'")
    except Exception as e:
        raise Exception(f"Failed to delete record: {str(e)}")


def search_global_top_k(vector_str: str, k: int, target_dbs: list) -> list:
    if not target_dbs:
        raise ValueError("target_dbs list cannot be empty.")
    for db_name in target_dbs:
        validate_table_name(db_name)
        
    try:
        vector = json.loads(vector_str)
        all_results = []
        
        for db_name in target_dbs:
            tbl = tables[db_name]
            results = tbl.search(vector).metric("cosine").limit(k).to_list()
            all_results.extend(results)
            
        all_results.sort(key=lambda x: x["_distance"])
        
        global_top_k = all_results[:k]
        
        return [item["data"] for item in global_top_k]
        
    except Exception as e:
        raise Exception(f"Global Top-K search failed: {str(e)}")


def search_by_threshold(vector_str: str, threshold: float, target_dbs: list) -> list:
    if not target_dbs:
        raise ValueError("target_dbs list cannot be empty.")
    for db_name in target_dbs:
        validate_table_name(db_name)
        
    try:
        vector = json.loads(vector_str)
        all_results = []
        
        for db_name in target_dbs:
            tbl = tables[db_name]
            results = tbl.search(vector).metric("cosine").limit(100).to_list()
            
            for item in results:
                similarity = 1.0 - item["_distance"]
                if similarity > threshold:
                    item["_similarity"] = similarity
                    all_results.append(item)
                    
        all_results.sort(key=lambda x: x["_similarity"], reverse=True)
        
        return [item["data"] for item in all_results]
    except Exception as e:
        raise Exception(f"Global Threshold search failed: {str(e)}")


def calculate_rerank_scores(query: str, targets: list) -> list:
    if not targets:
        return []
        
    scores = []
    
    instruction = "Given a web search query, retrieve relevant passages that answer the query"
    
    for target in targets:
        try:
            prompt = (
                "<|im_start|>system\n"
                "Judge whether the Document meets the requirements based on the Query and the Instruct provided. "
                "Note that the answer can only be \"yes\" or \"no\".<|im_end|>\n"
                "<|im_start|>user\n"
                f"<Instruct>: {instruction}\n"
                f"<Query>: {query}\n"
                f"<Document>: {target}<|im_end|>\n"
                "<|im_start|>assistant\n"
                "<think>\n\n</think>\n\n"
            )
            
            inputs = rerank_tokenizer(prompt, return_tensors="pt", max_length=8192, truncation=True).to(rerank_model.device)
            
            with torch.no_grad():
                outputs = rerank_model(**inputs)
            
            next_token_logits = outputs.logits[0, -1, :]
            yes_logit = next_token_logits[yes_id].item()
            no_logit = next_token_logits[no_id].item()
            
            logits_tensor = torch.tensor([yes_logit, no_logit], dtype=torch.float32)
            probabilities = torch.softmax(logits_tensor, dim=0)
            
            yes_probability = probabilities[0].item()
            scores.append(yes_probability)
            
        except Exception as e:
            print(f"Error calculating score for a target: {str(e)}")
            scores.append(0.0)
            
    return scores
