from bytez import Bytez
from datetime import datetime, timedelta
import json
import sqlite3
import os

class GroceryAssistant:
    def __init__(self, api_key, db_path='data/grocery.db'):
        self.sdk = Bytez(api_key)
        self.model = self.sdk.model("Qwen/Qwen3-0.6B")
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database with proper schema"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Purchases table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT NOT NULL,
                category TEXT,
                quantity INTEGER DEFAULT 1,
                unit_price REAL,
                purchase_date TEXT NOT NULL,
                expiry_date TEXT NOT NULL,
                consumed INTEGER DEFAULT 0
            )
        ''')
        
        # Shopping lists table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shopping_lists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT NOT NULL,
                quantity INTEGER DEFAULT 1,
                priority TEXT DEFAULT 'medium',
                added_date TEXT NOT NULL,
                completed INTEGER DEFAULT 0
            )
        ''')
        
        # AI interactions log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_type TEXT NOT NULL,
                user_input TEXT,
                ai_response TEXT,
                timestamp TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✓ Database initialized")
    
    def _call_ai_model(self, prompt):
        """Unified AI model caller with proper error handling"""
        try:
            response = self.model.run([{"role": "user", "content": prompt}])
            
            # Debug logging
            print(f"Response type: {type(response)}")
            
            # Bytez returns a Response object with .output and .error attributes
            if hasattr(response, 'error') and response.error:
                print(f"API Error: {response.error}")
                return None, str(response.error)
            
            if hasattr(response, 'output'):
                output = response.output
                print(f"Output type: {type(output)}")
                print(f"Output content: {output}")
                
                # output is a dict with 'role' and 'content'
                if isinstance(output, dict) and 'content' in output:
                    content = output['content']
                    
                    # Check if content is empty
                    if not content or content.strip() == '':
                        return None, "AI returned empty response"
                    
                    # Remove <think> tags if present
                    if '<think>' in content and '</think>' in content:
                        # Extract only the part after </think>
                        content = content.split('</think>')[-1].strip()
                    
                    return content, None
                
                # If output is a string directly
                if output:
                    return str(output), None
                else:
                    return None, "Empty output from AI"
            
            return None, "No output attribute in response"
            
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {e}")
            return None, f"JSON Error: {str(e)}"
        except Exception as e:
            print(f"AI Model Error: {e}")
            import traceback
            traceback.print_exc()
            return None, str(e)
    
    def add_purchase(self, item_name, quantity=1, expiry_days=7, category=None, unit_price=None):
        """Add purchase to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        purchase_date = datetime.now().isoformat()
        expiry_date = (datetime.now() + timedelta(days=expiry_days)).isoformat()
        
        # Use AI to categorize if not provided
        if not category:
            category = self._ai_categorize_item(item_name)
        
        cursor.execute('''
            INSERT INTO purchases (item_name, category, quantity, unit_price, purchase_date, expiry_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (item_name, category, quantity, unit_price, purchase_date, expiry_date))
        
        conn.commit()
        conn.close()
        print(f"✓ Added {item_name} ({category}) to database")
        return {"status": "success", "item": item_name, "category": category}
    
    def _ai_categorize_item(self, item_name):
        """Use AI to categorize grocery item"""
        prompt = f"""Categorize this grocery item into ONE category only: "{item_name}"

Categories: Produce, Dairy, Meat, Bakery, Pantry, Beverages, Snacks, Frozen, Other

Respond with ONLY the category name, nothing else."""
        
        output, error = self._call_ai_model(prompt)
        
        if error or not output:
            print(f"Categorization failed, using default: {error}")
            return "Other"
        
        category = output.strip()
        # Validate category
        valid_categories = ["Produce", "Dairy", "Meat", "Bakery", "Pantry", "Beverages", "Snacks", "Frozen", "Other"]
        for valid in valid_categories:
            if valid.lower() in category.lower():
                return valid
        
        return "Other"
    
    def get_all_purchases(self):
        """Retrieve all purchases from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM purchases ORDER BY purchase_date DESC')
        purchases = cursor.fetchall()
        conn.close()
        
        result = []
        for p in purchases:
            result.append({
                "id": p[0],
                "item_name": p[1],
                "category": p[2],
                "quantity": p[3],
                "unit_price": p[4],
                "purchase_date": p[5],
                "expiry_date": p[6],
                "consumed": p[7]
            })
        return result
    
    def predict_missing_items(self):
        """AI predicts missing items based on REAL purchase history from database"""
        purchases = self.get_all_purchases()
        
        if not purchases:
            return "No purchase history available. Start adding items to get AI predictions!"
        
        # Build simplified context (limit items)
        recent_items = []
        for p in purchases[:10]:
            days_ago = (datetime.now() - datetime.fromisoformat(p['purchase_date'])).days
            recent_items.append(f"{p['item_name']} - {days_ago} days ago")
        
        items_text = "\n".join(recent_items)
        
        prompt = f"""Recent grocery purchases:
{items_text}

Today: {datetime.now().strftime('%Y-%m-%d')}

Based on this, suggest 5 items the user should buy again. For each item explain why."""
        
        output, error = self._call_ai_model(prompt)
        
        if error:
            print(f"Prediction error: {error}")
            # Provide basic prediction as fallback
            return self._basic_prediction(purchases)
        
        if not output:
            return self._basic_prediction(purchases)
        
        # Log AI interaction
        self._log_ai_interaction("predict_missing", items_text, output)
        
        return f"🔮 AI PREDICTIONS:\n\n{output}"
    
    def _basic_prediction(self, purchases):
        """Fallback: Basic prediction without AI"""
        old_items = []
        for p in purchases:
            days_ago = (datetime.now() - datetime.fromisoformat(p['purchase_date'])).days
            if days_ago >= 7:
                old_items.append(f"• {p['item_name']} (purchased {days_ago} days ago)")
        
        if old_items:
            return f"""🔮 ITEMS TO RESTOCK:

{chr(10).join(old_items[:7])}

These items were purchased over a week ago and might need restocking."""
        else:
            return "Your recent purchases are still fresh. Check back in a few days!"
    
    def suggest_healthy_alternatives(self, item_name):
        """AI suggests healthy alternatives based on database and nutrition knowledge"""
        if not item_name or item_name.strip() == '':
            return "Please provide an item name to find alternatives for."
        
        # Get purchase history of this item
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM purchases WHERE item_name LIKE ? ORDER BY purchase_date DESC LIMIT 5', 
                      (f'%{item_name}%',))
        history = cursor.fetchall()
        conn.close()
        
        history_note = f"You've purchased this {len(history)} times." if history else ""
        
        prompt = f"""Suggest 3 healthier alternatives for: {item_name}

{history_note}

For each alternative, briefly explain the health benefits."""
        
        output, error = self._call_ai_model(prompt)
        
        if error:
            print(f"Alternatives error: {error}")
            return self._basic_alternatives(item_name)
        
        if not output:
            return self._basic_alternatives(item_name)
        
        self._log_ai_interaction("healthy_alternatives", item_name, output)
        return f"🥗 HEALTHIER OPTIONS FOR '{item_name}':\n\n{output}"
    
    def _basic_alternatives(self, item_name):
        """Fallback: Basic alternatives suggestions"""
        common_swaps = {
            'bread': 'whole grain bread, multigrain bread, sourdough',
            'milk': 'almond milk, oat milk, low-fat milk',
            'sugar': 'honey, stevia, maple syrup',
            'soda': 'sparkling water, coconut water, herbal tea',
            'chips': 'veggie chips, popcorn, nuts',
            'white rice': 'brown rice, quinoa, cauliflower rice'
        }
        
        for key, alternatives in common_swaps.items():
            if key in item_name.lower():
                return f"""🥗 HEALTHIER ALTERNATIVES FOR '{item_name}':

Consider these options:
• {alternatives.replace(', ', chr(10) + '• ')}

These alternatives typically offer better nutrition with more fiber, vitamins, or less processing."""
        
        return f"""🥗 For '{item_name}', consider:

• Look for whole grain versions
• Choose organic or less processed options
• Check for lower sugar/sodium alternatives
• Consider plant-based substitutes

Add prices to your purchases for personalized budget-friendly suggestions!"""
    
    def check_expiring_items(self):
        """AI analyzes REAL expiring items from database and suggests recipes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get items expiring in next 3 days
        three_days_later = (datetime.now() + timedelta(days=3)).isoformat()
        cursor.execute('''
            SELECT item_name, category, quantity, expiry_date 
            FROM purchases 
            WHERE expiry_date <= ? AND consumed = 0
            ORDER BY expiry_date
        ''', (three_days_later,))
        
        expiring = cursor.fetchall()
        conn.close()
        
        if not expiring:
            return "✓ Great! No items expiring in the next 3 days."
        
        # Build detailed context (limit to prevent too long prompts)
        expiring_details = []
        for item in expiring[:10]:  # Limit to 10 items
            days_left = (datetime.fromisoformat(item[3]) - datetime.now()).days
            expiring_details.append(f"- {item[0]} ({item[1]}) - {days_left} days left")
        
        expiring_text = "\n".join(expiring_details)
        
        prompt = f"""These grocery items are expiring soon:
{expiring_text}

Provide 2-3 quick recipe ideas using these items. Be concise and practical."""
        
        output, error = self._call_ai_model(prompt)
        
        if error:
            print(f"Expiring items error: {error}")
            return f"⚠️ Found {len(expiring)} expiring items:\n{expiring_text}\n\nUse these items soon to avoid waste!"
        
        if not output:
            return f"⚠️ Found {len(expiring)} expiring items:\n{expiring_text}"
        
        self._log_ai_interaction("expiring_items", expiring_text, output)
        return f"⚠️ EXPIRING ITEMS:\n{expiring_text}\n\n🍳 AI SUGGESTIONS:\n{output}"
    
    def create_smart_shopping_list(self, items_to_add):
        """AI creates optimized shopping list with smart suggestions"""
        if not items_to_add:
            return "No items provided for shopping list."
        
        # Get current inventory (limit to prevent long prompts)
        purchases = self.get_all_purchases()
        current_items = [p['item_name'] for p in purchases[:20] if not p['consumed']]
        
        items_text = ', '.join(items_to_add)
        current_text = ', '.join(current_items[:10]) if current_items else 'None'
        
        prompt = f"""Create a shopping list for: {items_text}

Current items at home: {current_text}

Organize by sections (Produce, Dairy, Meat, etc.) and suggest complementary items."""
        
        output, error = self._call_ai_model(prompt)
        
        if error:
            print(f"Shopping list error: {error}")
            # Return basic organized list as fallback
            return self._create_basic_shopping_list(items_to_add)
        
        if not output:
            return self._create_basic_shopping_list(items_to_add)
        
        # Add items to shopping_lists table
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            for item in items_to_add:
                cursor.execute('''
                    INSERT INTO shopping_lists (item_name, added_date)
                    VALUES (?, ?)
                ''', (item, datetime.now().isoformat()))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Database error: {e}")
        
        self._log_ai_interaction("shopping_list", str(items_to_add), output)
        return output
    
    def _create_basic_shopping_list(self, items):
        """Fallback: Create basic shopping list without AI"""
        return f"""📝 SHOPPING LIST:

Items to buy:
{chr(10).join([f'• {item}' for item in items])}

Total items: {len(items)}

💡 Tip: Check your pantry before shopping!"""
    
    def meal_planning_suggestions(self):
        """AI generates meal plans based on REAL current inventory"""
        purchases = self.get_all_purchases()
        
        if not purchases:
            return "No items in your inventory. Add purchases to get meal suggestions!"
        
        # Get fresh items (not expired, not consumed) - limit to 10
        available_items = []
        for p in purchases:
            if not p['consumed'] and datetime.fromisoformat(p['expiry_date']) > datetime.now():
                available_items.append(p['item_name'])
                if len(available_items) >= 10:
                    break
        
        if not available_items:
            return "No fresh items available for meal planning. Add some groceries first!"
        
        items_text = ", ".join(available_items)
        
        prompt = f"""Available ingredients: {items_text}

Suggest 3 meal ideas using these ingredients. For each meal:
- Meal name
- Main ingredients needed
- Quick cooking steps"""
        
        output, error = self._call_ai_model(prompt)
        
        if error:
            print(f"Meal planning error: {error}")
            return self._basic_meal_ideas(available_items)
        
        if not output:
            return self._basic_meal_ideas(available_items)
        
        self._log_ai_interaction("meal_planning", items_text, output)
        return f"🍳 MEAL IDEAS FROM YOUR GROCERIES:\n\n{output}"
    
    def _basic_meal_ideas(self, items):
        """Fallback: Basic meal suggestions"""
        return f"""🍳 MEAL IDEAS:

Your available ingredients: {', '.join(items)}

BREAKFAST IDEAS:
• Scrambled eggs with toast
• Oatmeal with fresh fruit
• Yogurt parfait

LUNCH IDEAS:
• Fresh salad with protein
• Sandwich with vegetables
• Soup with bread

DINNER IDEAS:
• Grilled/baked protein with vegetables
• Stir-fry with available ingredients
• Pasta with simple sauce

💡 Tip: Combine ingredients creatively based on what you have!"""
    
    def ai_chat(self, user_query):
        """General AI assistant for any grocery-related questions"""
        if not user_query or user_query.strip() == '':
            return "Please ask a question about your groceries."
        
        purchases = self.get_all_purchases()
        
        # Limit context to prevent too long prompts
        if purchases:
            context = self._build_purchase_summary(purchases[:10])
        else:
            context = "No purchase history yet."
        
        prompt = f"""User's recent purchases:
{context}

Question: {user_query}

Provide a helpful response."""
        
        output, error = self._call_ai_model(prompt)
        
        if error:
            print(f"Chat error: {error}")
            return f"I understand your question: '{user_query}'\n\nHowever, I'm having trouble generating a response right now. Please try rephrasing your question or ask something more specific about your groceries."
        
        if not output:
            return "I couldn't process your question. Please try again with a different question."
        
        self._log_ai_interaction("chat", user_query, output)
        return output
    
    def get_spending_analysis(self):
        """AI analyzes spending patterns from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT category, SUM(unit_price * quantity) as total FROM purchases WHERE unit_price IS NOT NULL GROUP BY category')
        spending = cursor.fetchall()
        
        cursor.execute('SELECT COUNT(*), SUM(unit_price * quantity) FROM purchases WHERE unit_price IS NOT NULL')
        totals = cursor.fetchone()
        conn.close()
        
        if not spending or not totals[0]:
            return "No spending data available. Add prices when logging purchases to get budget analysis!"
        
        spending_details = "\n".join([f"- {cat}: ${total:.2f}" for cat, total in spending[:10]])
        total_spent = totals[1] if totals[1] else 0
        
        prompt = f"""Analyze this grocery spending:

{spending_details}
Total: ${total_spent:.2f}

Provide budget tips and identify where user might save money."""
        
        output, error = self._call_ai_model(prompt)
        
        if error:
            print(f"Spending analysis error: {error}")
            return f"""💰 SPENDING SUMMARY:

{spending_details}

Total Items: {totals[0]}
Total Spent: ${total_spent:.2f}

💡 Consider tracking prices to find better deals and identify overspending categories."""
        
        if not output:
            return f"""💰 SPENDING SUMMARY:

{spending_details}

Total: ${total_spent:.2f}"""
        
        return f"""💰 SPENDING SUMMARY:
{spending_details}
Total: ${total_spent:.2f}

📊 AI ANALYSIS:
{output}"""
    
    def _build_purchase_summary(self, purchases):
        """Build a comprehensive summary for AI context"""
        if not purchases:
            return "No purchase history."
        
        summary_lines = []
        for p in purchases[:20]:  # Last 20 purchases
            days_ago = (datetime.now() - datetime.fromisoformat(p['purchase_date'])).days
            summary_lines.append(
                f"- {p['item_name']} ({p['category']}) - {days_ago} days ago, expires in {(datetime.fromisoformat(p['expiry_date']) - datetime.now()).days} days"
            )
        
        return "\n".join(summary_lines)
    
    def _log_ai_interaction(self, query_type, user_input, ai_response):
        """Log AI interactions to database for learning"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Ensure ai_response is a string
            response_text = str(ai_response) if ai_response else ""
            
            cursor.execute('''
                INSERT INTO ai_logs (query_type, user_input, ai_response, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (query_type, str(user_input)[:500], response_text[:1000], datetime.now().isoformat()))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Logging error (non-critical): {e}")
    
    def get_statistics(self):
        """Get statistics from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM purchases')
        total_items = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(DISTINCT category) FROM purchases')
        categories = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM purchases WHERE consumed = 1')
        consumed = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_items": total_items,
            "categories": categories,
            "consumed_items": consumed,
            "active_items": total_items - consumed
        }


# Example usage
if __name__ == "__main__":
    assistant = GroceryAssistant("c34ee9824b16cec9a0837b7e66aad9f4")
    
    print("=" * 60)
    print("🛒 AI-POWERED SMART GROCERY ASSISTANT")
    print("=" * 60)
    
    # Add sample data with prices
    print("\n📦 Adding sample purchases...")
    assistant.add_purchase("whole milk", quantity=1, expiry_days=5, unit_price=3.99)
    assistant.add_purchase("white bread", quantity=1, expiry_days=7, unit_price=2.49)
    assistant.add_purchase("organic eggs", quantity=12, expiry_days=2, unit_price=5.99)
    
    # Statistics
    stats = assistant.get_statistics()
    print(f"\n📊 Statistics: {stats}")
    
    # Test AI
    print("\n" + "=" * 60)
    print("🔮 Testing AI:")
    print("=" * 60)
    print(assistant.predict_missing_items())