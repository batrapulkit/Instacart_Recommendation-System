from flask import Flask, jsonify, request
import pickle
import pandas as pd
import logging

# Initialize the Flask app
app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Load the recommender model
try:
    with open('recommender_model.pkl', 'rb') as f:
        recommender_model = pickle.load(f)
    app.logger.info("Recommender model loaded successfully.")
except Exception as e:
    app.logger.error(f"Error loading recommender model: {e}")
    recommender_model = None

# Load CSV files
try:
    order_products = pd.read_csv('order_products.csv')
    orders = pd.read_csv('orders.csv')
    products = pd.read_csv('products.csv')

    # Merge orders to include `user_id` in `order_products`
    order_products = order_products.merge(orders[['order_id', 'user_id']], on='order_id', how='left')
    app.logger.info("CSV files loaded and merged successfully.")
except Exception as e:
    app.logger.error(f"Error loading CSV files: {e}")
    order_products, orders, products = None, None, None

@app.route('/recommend', methods=['GET'])
def recommend():
    # Get user_id from query parameters
    user_id = request.args.get('user_id', type=int)

    if user_id is None:
        return jsonify({'error': 'user_id is required'}), 400

    if order_products is None or products is None:
        return jsonify({'error': 'Data not loaded correctly. Please check server logs.'}), 500

    try:
        # Ensure the user exists in the dataset
        if user_id not in order_products['user_id'].values:
            return jsonify({'error': f'User {user_id} not found'}), 404

        # Find the products the user has already ordered
        user_orders = order_products[order_products['user_id'] == user_id]
        user_ordered_product_ids = user_orders['product_id'].tolist()

        # Find products ordered by similar users, excluding already ordered ones
        similar_users_products = order_products[
            (order_products['product_id'].isin(user_ordered_product_ids)) & 
            (order_products['user_id'] != user_id)
        ]
        recommended_product_ids = similar_users_products['product_id'].value_counts().head(5).index.tolist()

        # If no recommendations found
        if len(recommended_product_ids) == 0:
            return jsonify({'error': 'No recommendations found for this user'}), 404

        # Fetch details of recommended products
        recommended_products_details = products[products['product_id'].isin(recommended_product_ids)]

        # Convert to a list of dictionaries
        recommended_products_list = recommended_products_details.to_dict(orient='records')

        return jsonify({'user_id': user_id, 'recommended_products': recommended_products_list})

    except Exception as e:
        app.logger.error(f"Error during recommendation: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/')
def home():
    return "Recommender API is running!"

if __name__ == '__main__':
    app.run(debug=True)
