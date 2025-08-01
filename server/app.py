from flask import Flask
from flask_cors import CORS
from routes import portfolio_bp
from db import init_db
from flask import Flask, send_from_directory
import os

app = Flask(__name__, static_folder='../client')
CORS(app)  # Enable CORS for all routes
app.register_blueprint(portfolio_bp)

@app.route('/portfoliotable')
def portfolio():
    return send_from_directory(app.static_folder, 'portfoliotable.html')

@app.route('/homebroker')
def homebroker():
    return send_from_directory(app.static_folder, 'homebroker.html')

@app.route('/test-users')
def test_users():
    return send_from_directory(app.static_folder, 'test_users.html')

@app.route('/<path:filename>')
def serve_static(filename):
    # Make sure the file exists inside the static folder
    file_path = os.path.join(app.static_folder, filename)
    return send_from_directory(app.static_folder, filename)


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)