#!/usr/bin/env python3
"""
Splice3D API Server - Stub for Render deployment
The main splice3d functionality runs locally. This provides status info.
"""

from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "splice3d-api",
        "message": "Splice3D API stub - Core functionality runs locally"
    })

@app.route('/', methods=['GET'])
def index():
    """Landing page"""
    return jsonify({
        "service": "Splice3D API",
        "description": "Multi-material 3D printing post-processor",
        "status": "stub",
        "note": "Core functionality (G-code processing) runs locally",
        "docs": "https://github.com/dmhernandez2525/splice3d",
        "endpoints": {
            "/health": "Health check",
            "/": "This page"
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
