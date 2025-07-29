from flask import Blueprint, request, jsonify

portfolio_bp = Blueprint('portfolio', __name__)

@portfolio_bp.route('/balance', methods=['GET'])
def get_balance():
    ...

@portfolio_bp.route('/buy', methods=['POST'])
def buy_stock():
    ...

@portfolio_bp.route('/sell', methods=['POST'])
def sell_stock():
    ...
