# app/routes.py
from flask import Blueprint, jsonify, request
import sys
import platform
import torch
import os
from datetime import datetime

from services.tts_service import generate_tts_from_reference, run_test_script

bp = Blueprint('api', __name__, url_prefix='/')

@bp.route('/tts/generate', methods=['POST'])
def handle_tts_generation():
    data = request.get_json()
    if not data or 'reference_audio_path' not in data or 'text' not in data:
        return jsonify({"status": "error", "message": "Request body must contain 'reference_audio_path' and 'text'"}), 400

    ref_path = data['reference_audio_path']
    text = data['text']
    ref_text = data.get('ref_text', None)

    output_path, error = generate_tts_from_reference(ref_path, text, ref_text)

    if error:
        return jsonify({"status": "error", "message": error}), 500
    
    return jsonify({
        "status": "success",
        "message": "Audio generated successfully.",
        "generated_audio_path": output_path
    }), 200

@bp.route('/ping', methods=['GET'])
def ping():
    return jsonify({"status": "ok", "message": "Python server is alive!", "timestamp": datetime.now().isoformat()})

@bp.route('/health', methods=['GET'])
def health():
    gpu_available = torch.cuda.is_available()
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "python_version": platform.python_version(),
        "gpu_available": gpu_available,
        "gpu_name": torch.cuda.get_device_name(0) if gpu_available else "N/A",
    })

@bp.route('/test', methods=['POST'])
def handle_test():
    data = request.get_json()
    script_name = data.get('script')
    if script_name not in ['full', 'rerank']:
        return jsonify({"status": "error", "message": "Invalid script name. Must be 'full' or 'rerank'"}), 400
        
    result = run_test_script(script_name)
    status_code = 500 if result['status'] in ['error', 'timeout'] else 200
    return jsonify(result), status_code

from services.rag_service import (
    text_to_embedding_str,
    insert_to_db,
    search_global_top_k,
    search_by_threshold,
    delete_by_data,
    calculate_rerank_scores
)

# --- 新增: RAG 相关的 API 接口 ---

@bp.route('/rag/embed', methods=['POST'])
def rag_embed():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({"status": "error", "message": "Missing 'text' in request"}), 400
    
    try:
        vector_str = text_to_embedding_str(data['text'])
        return jsonify({"status": "success", "vector_str": vector_str}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@bp.route('/rag/insert', methods=['POST'])
def rag_insert():
    data = request.get_json()
    if not data or 'vector_str' not in data or 'data_str' not in data or 'table_name' not in data:
        return jsonify({"status": "error", "message": "Missing 'vector_str', 'data_str', or 'table_name'"}), 400
    try:
        insert_to_db(data['vector_str'], data['data_str'], data['table_name'])
        return jsonify({"status": "success", "message": "Data inserted successfully."}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@bp.route('/rag/search/topk', methods=['POST'])
def rag_search_topk():
    data = request.get_json()
    if not data or 'vector_str' not in data or 'k' not in data or 'target_dbs' not in data:
        return jsonify({"status": "error", "message": "Missing required parameters"}), 400
    try:
        k = int(data['k'])
        target_dbs = data['target_dbs']
        results = search_global_top_k(data['vector_str'], k, target_dbs)
        return jsonify({"status": "success", "results": results}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@bp.route('/rag/search/threshold', methods=['POST'])
def rag_search_threshold():
    data = request.get_json()
    if not data or 'vector_str' not in data or 'threshold' not in data or 'target_dbs' not in data:
        return jsonify({"status": "error", "message": "Missing required parameters"}), 400
    try:
        threshold = float(data['threshold'])
        target_dbs = data['target_dbs']
        results = search_by_threshold(data['vector_str'], threshold, target_dbs)
        return jsonify({"status": "success", "results": results}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@bp.route('/rag/delete', methods=['POST'])
def rag_delete():
    data = request.get_json()
    if not data or 'data_str' not in data or 'table_name' not in data:
        return jsonify({"status": "error", "message": "Missing 'data_str' or 'table_name'"}), 400
    try:
        delete_by_data(data['data_str'], data['table_name'])
        return jsonify({"status": "success", "message": "Deleted successfully."}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@bp.route('/rag/rerank', methods=['POST'])
def rag_rerank():
    data = request.get_json()
    if not data or 'query' not in data or 'targets' not in data:
        return jsonify({"status": "error", "message": "Missing 'query' or 'targets' in request"}), 400
    
    try:
        query = data['query']
        targets = data['targets']
        
        if not isinstance(targets, list):
            return jsonify({"status": "error", "message": "'targets' must be a list of strings"}), 400
            
        scores = calculate_rerank_scores(query, targets)
        return jsonify({"status": "success", "scores": scores}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
