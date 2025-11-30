from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from grocery_assistant import GroceryAssistant

app = Flask(__name__, static_folder='../frontend')
CORS(app)

# Initialize AI assistant with database
assistant = GroceryAssistant("c34ee9824b16cec9a0837b7e66aad9f4", db_path='../data/grocery.db')

# Serve frontend
@app.route('/')
def serve_frontend():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/add-purchase', methods=['POST'])
def add_purchase():
    """Add purchase with AI categorization"""
    try:
        data = request.json
        result = assistant.add_purchase(
            item_name=data['item'],
            quantity=data.get('quantity', 1),
            expiry_days=data.get('expiry_days', 7),
            category=data.get('category'),
            unit_price=data.get('unit_price')
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/purchases', methods=['GET'])
def get_purchases():
    """Get all purchases from database"""
    try:
        purchases = assistant.get_all_purchases()
        return jsonify({"purchases": purchases})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/predict', methods=['GET'])
def predict_items():
    """AI predicts missing items based on real database data"""
    try:
        result = assistant.predict_missing_items()
        return jsonify({"result": result, "type": "ai_response"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/alternatives', methods=['POST'])
def get_alternatives():
    """AI suggests healthy alternatives"""
    try:
        item = request.json.get('item')
        if not item:
            return jsonify({"error": "Item name required"}), 400
        
        result = assistant.suggest_healthy_alternatives(item)
        return jsonify({"result": result, "type": "ai_response"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/expiring', methods=['GET'])
def check_expiring():
    """AI analyzes expiring items from database"""
    try:
        result = assistant.check_expiring_items()
        return jsonify({"result": result, "type": "ai_response"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/shopping-list', methods=['POST'])
def create_list():
    """AI creates optimized shopping list"""
    try:
        items = request.json.get('items', [])
        if not items:
            return jsonify({"error": "Items required"}), 400
        
        result = assistant.create_smart_shopping_list(items)
        return jsonify({"result": result, "type": "ai_response"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/meal-ideas', methods=['GET'])
def meal_ideas():
    """AI generates meal ideas from real inventory"""
    try:
        result = assistant.meal_planning_suggestions()
        return jsonify({"result": result, "type": "ai_response"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/spending-analysis', methods=['GET'])
def spending_analysis():
    """AI analyzes spending patterns"""
    try:
        result = assistant.get_spending_analysis()
        return jsonify({"result": result, "type": "ai_response"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def ai_chat():
    """General AI chat for any grocery questions"""
    try:
        query = request.json.get('query')
        if not query:
            return jsonify({"error": "Query required"}), 400
        
        result = assistant.ai_chat(query)
        return jsonify({"result": result, "type": "ai_response"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get database statistics"""
    try:
        stats = assistant.get_statistics()
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/mark-consumed', methods=['POST'])
def mark_consumed():
    """Mark item as consumed"""
    try:
        item_id = request.json.get('id')
        if not item_id:
            return jsonify({"error": "Item ID required"}), 400
        
        # Update database
        import sqlite3
        conn = sqlite3.connect(assistant.db_path)
        cursor = conn.cursor()
        cursor.execute('UPDATE purchases SET consumed = 1 WHERE id = ?', (item_id,))
        conn.commit()
        conn.close()
        
        return jsonify({"status": "success", "message": "Item marked as consumed"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 STARTING AI-POWERED GROCERY ASSISTANT")
    print("="*60)
    print("📱 Frontend: http://localhost:5000")
    print("🤖 AI Engine: Qwen3-0.6B (Bytez)")
    print("💾 Database: SQLite")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)