from flask import Flask
from flask_cors import CORS
from routes import portfolio_bp
from db import init_db

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.register_blueprint(portfolio_bp)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)