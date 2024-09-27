#!/usr/bin/env python3

import papermill as pm
from flask import Flask, request, jsonify
import json
import uuid
import time

app = Flask(__name__)

requests_history = []

def generate_request_id():
    return str(uuid.uuid4())


def extract_results(file_path):
    """Extracts the 'output' field from the dictionary within the 'cells' array where the 'tags' array contains 'results'.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        list: A list of 'output' values.
    """

    with open(file_path, 'r') as f:
        data = json.load(f)

    results = []
    for cell in data['cells']:
        if 'tags' in cell['metadata'] and 'results' in cell['metadata']['tags']:
            results.append(cell['outputs'][0]['text'][0])

    return results


def process_request(variable_dict, request_id):
    pm.execute_notebook(
    'service.ipynb',
    f'output-{request_id}.json',
    parameters = variable_dict,
    progress_bar=False
    )

    file_path = f'output-{request_id}.json'
    results = extract_results(file_path)

    return results[0]


@app.route('/request', methods=['POST'])
def submit_request():
    '''Submit request for the service.

    The input is expected in JSON format:
    {
        "inputs": {
            "variable0": "value0",
            "variable1": "value1",
            "variable2": "value2",
            "variable3": "value3",
            ...
        }
    }
    '''
    data = request.get_json()
    request_id = generate_request_id()
    timestamp = time.time()

    # Process the request and generate a result
    try:
        result = process_request(data["inputs"], request_id=request_id)
    except Exception as e:
        return jsonify({'error': repr(e)}), 404

    # Store the request and response in history
    requests_history.append({
        'request_id': request_id,
        'timestamp': timestamp,
        'request': data,
        'result': result
    })

    return jsonify({'request_id': request_id, 'result': result})


@app.route('/request/<request_id>', methods=['GET'])
def query_request(request_id):
    for request_data in requests_history:
        if request_data['request_id'] == request_id:
            return jsonify(request_data)

    return jsonify({'error': 'Request not found'}), 404


if __name__ == '__main__':
    app.run(debug=True, port=5050)
