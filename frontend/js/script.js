// Simulated purchase history (in real app, this would connect to your Python backend)
        let purchaseHistory = [];

        function addPurchase() {
            const itemName = document.getElementById('itemName').value.trim();
            const quantity = document.getElementById('quantity').value;
            const expiryDays = document.getElementById('expiryDays').value;

            if (!itemName) {
                alert('Please enter an item name');
                return;
            }

            const purchase = {
                item: itemName,
                quantity: quantity,
                purchaseDate: new Date().toISOString(),
                expiryDate: new Date(Date.now() + expiryDays * 24 * 60 * 60 * 1000).toISOString(),
                expiryDays: parseInt(expiryDays)
            };

            purchaseHistory.push(purchase);
            updateHistoryDisplay();

            // Clear form
            document.getElementById('itemName').value = '';
            document.getElementById('quantity').value = '1';

            // Show success feedback
            alert(`✓ ${itemName} added to purchase history!`);
        }

        function updateHistoryDisplay() {
            const historyList = document.getElementById('historyList');
            
            if (purchaseHistory.length === 0) {
                historyList.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-icon">🛍️</div>
                        <p>No purchases yet. Add your first item!</p>
                    </div>
                `;
                return;
            }

            historyList.innerHTML = purchaseHistory.map((item, index) => {
                const daysUntilExpiry = Math.floor((new Date(item.expiryDate) - new Date()) / (1000 * 60 * 60 * 24));
                const isExpiring = daysUntilExpiry <= 3;
                const badgeClass = isExpiring ? 'badge-expiring' : 'badge-fresh';
                const badgeText = isExpiring ? `Expires in ${daysUntilExpiry}d` : 'Fresh';

                return `
                    <li class="history-item">
                        <div class="history-item-info">
                            <div class="history-item-name">${item.item} (x${item.quantity})</div>
                            <div class="history-item-date">Added: ${new Date(item.purchaseDate).toLocaleDateString()}</div>
                        </div>
                        <span class="badge ${badgeClass}">${badgeText}</span>
                    </li>
                `;
            }).join('');
        }

        async function predictMissingItems() {
            const resultsDiv = document.getElementById('predictResults');
            const contentDiv = resultsDiv.querySelector('.results-content');
            
            if (purchaseHistory.length === 0) {
                alert('Please add some purchases first!');
                return;
            }

            resultsDiv.style.display = 'block';
            contentDiv.innerHTML = '<div class="loading">🤖 AI is analyzing your purchase patterns...</div>';

            // Simulate API call to Python backend
            setTimeout(() => {
                // This would be a real API call to your Python backend
                const mockResponse = `Based on your purchase history, you might need:

• Milk - Last purchased ${Math.floor(Math.random() * 7) + 1} days ago
• Eggs - Commonly purchased weekly item
• Bread - Running low based on typical consumption
• Fresh vegetables - Good time to restock

Would you like to add these to your shopping list?`;
                
                contentDiv.innerHTML = mockResponse;
            }, 2000);
        }

        async function getHealthyAlternatives() {
            const item = document.getElementById('alternativeItem').value.trim();
            const resultsDiv = document.getElementById('alternativeResults');
            const contentDiv = resultsDiv.querySelector('.results-content');

            if (!item) {
                alert('Please enter an item to find alternatives for');
                return;
            }

            resultsDiv.style.display = 'block';
            contentDiv.innerHTML = '<div class="loading">🤖 Finding healthier alternatives...</div>';

            setTimeout(() => {
                const mockResponse = `Healthier alternatives for "${item}":

• Whole grain bread
  → More fiber, vitamins, and minerals than white bread
  
• Almond milk
  → Lower calories, lactose-free, rich in vitamin E
  
• Quinoa pasta
  → Higher protein content, gluten-free option

These alternatives offer better nutritional value while maintaining great taste!`;
                
                contentDiv.innerHTML = mockResponse;
            }, 2000);
        }

        async function checkExpiringItems() {
            const resultsDiv = document.getElementById('expiringResults');
            const contentDiv = resultsDiv.querySelector('.results-content');

            if (purchaseHistory.length === 0) {
                alert('Please add some purchases first!');
                return;
            }

            resultsDiv.style.display = 'block';
            contentDiv.innerHTML = '<div class="loading">🤖 Checking expiration dates...</div>';

            setTimeout(() => {
                const expiringItems = purchaseHistory.filter(item => {
                    const daysLeft = Math.floor((new Date(item.expiryDate) - new Date()) / (1000 * 60 * 60 * 24));
                    return daysLeft <= 3 && daysLeft >= 0;
                });

                if (expiringItems.length === 0) {
                    contentDiv.innerHTML = '✓ Great news! No items expiring in the next 3 days.';
                } else {
                    const mockResponse = `⚠️ Items expiring soon:

${expiringItems.map(item => {
    const daysLeft = Math.floor((new Date(item.expiryDate) - new Date()) / (1000 * 60 * 60 * 24));
    return `• ${item.item}: ${daysLeft} day(s) left
  Try: Make a smoothie or stir-fry`;
}).join('\n\n')}

Use these items soon to avoid waste!`;
                    contentDiv.innerHTML = mockResponse;
                }
            }, 2000);
        }

        async function createShoppingList() {
            const items = document.getElementById('shoppingItems').value.trim();
            const resultsDiv = document.getElementById('shoppingResults');
            const contentDiv = resultsDiv.querySelector('.results-content');

            if (!items) {
                alert('Please enter items for your shopping list');
                return;
            }

            resultsDiv.style.display = 'block';
            contentDiv.innerHTML = '<div class="loading">🤖 Organizing your shopping list...</div>';

            setTimeout(() => {
                const mockResponse = `📝 Organized Shopping List:

🥬 PRODUCE:
• Apples

🥛 DAIRY:
• Milk

🍞 BAKERY:
• Bread

🍗 MEAT & POULTRY:
• Chicken

💡 Tip: Don't forget reusable bags!
⚠️ Health Note: Consider whole grain bread instead of white bread`;
                
                contentDiv.innerHTML = mockResponse;
            }, 2000);
        }

        async function getMealIdeas() {
            const resultsDiv = document.getElementById('mealResults');
            const contentDiv = resultsDiv.querySelector('.results-content');

            if (purchaseHistory.length === 0) {
                alert('Please add some purchases first!');
                return;
            }

            resultsDiv.style.display = 'block';
            contentDiv.innerHTML = '<div class="loading">🤖 Generating meal ideas from your groceries...</div>';

            setTimeout(() => {
                const mockResponse = `🍳 Meal Ideas Based on Your Groceries:

MEAL 1: Quick Breakfast Bowl
Ingredients: Eggs, milk, bread
Steps: Scramble eggs with milk, serve with toasted bread

MEAL 2: Healthy Salad
Ingredients: Spinach, chicken, olive oil
Steps: Grill chicken, toss with fresh spinach and light dressing

MEAL 3: Protein Smoothie
Ingredients: Yogurt, milk, any fruits
Steps: Blend all ingredients until smooth

Enjoy your meals! 😋`;
                
                contentDiv.innerHTML = mockResponse;
            }, 2000);
        }

        // Initialize
        updateHistoryDisplay();