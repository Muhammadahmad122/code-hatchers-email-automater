from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "system": "Code Hatchers Email Automater",
        "version": "1.3-vercel"
    })

# Vercel requires a handler
def handler(request):
    return app(request)
