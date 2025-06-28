from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({
        'message': 'Welcome to the Python API!',
        'status': 'running'
    })

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'python-api'
    })

@app.route('/api/hello')
def hello():
    return jsonify({
        'message': 'Hello from Python API!',
        'timestamp': '2024-01-01T00:00:00Z'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True) 