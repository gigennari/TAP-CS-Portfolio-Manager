from flask import Flask
from routes import portfolio_bp
from db import init_db

app = Flask(__name__)
app.register_blueprint(portfolio_bp)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)