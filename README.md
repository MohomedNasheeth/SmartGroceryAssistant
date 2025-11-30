# 🛒 Smart Grocery Assistant

An intelligent grocery recommendation system powered by AI that helps users discover and organize their shopping needs through a simple web interface.

![Home Interface](https://img.shields.io/badge/Status-Active-success)
![API](https://img.shields.io/badge/API-Running-blue)
![Python](https://img.shields.io/badge/Python-3.10+-yellow)

## 🚀 Features

- ✅ **AI-Based Recommendations** - Smart grocery suggestions based on user input
- ✅ **Responsive Web Frontend** - Clean and intuitive user interface
- ✅ **REST API Backend** - Flask-powered API for seamless integration
- ✅ **SQLite Database** - Efficient local data storage
- ✅ **Virtual Environment** - Isolated dependency management
- ✅ **Lightweight & Fast** - Optimized performance for quick responses

## 🏗 Project Structure

```
Smart_Grocery/
├── backend/
│   ├── grocery_assistant.py    # Core AI logic
│   └── app.py                  # Flask API server
├── frontend/
│   └── index.html              # Web interface
├── data/
│   └── grocery.db              # SQLite database
├── .venv/                      # Virtual environment
├── run.py                      # Application starter
└── README.md                   # Documentation
```

## 🔧 Installation & Setup

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

### Step 1: Create Virtual Environment

```bash
python -m venv .venv
```

### Step 2: Activate Virtual Environment

**Windows:**
```bash
.venv\Scripts\activate
```

**Linux / macOS:**
```bash
source .venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install flask flask-cors bytez
```

### Step 4: Run the Application

```bash
python run.py
```

### Step 5: Open in Browser

Navigate to:
```
http://localhost:5000
```


## 🤖 Technology Stack

| Technology | Purpose |
|------------|---------|
| **Python 3.10+** | Core programming language |
| **Flask** | Web framework and API |
| **HTML/CSS/JS** | Frontend interface |
| **SQLite** | Database management |
| **Bytez** | AI logic integration |
| **Flask-CORS** | Cross-origin resource sharing |


## 🎯 Usage Example

1. Open the web interface at `http://localhost:5000`
2. Enter your grocery needs (e.g., "ingredients for dinner tonight")
3. Receive AI-powered suggestions
4. View your prediction history
5. Export or save your grocery list

## 📌 Future Improvements

- 🔹 **User Authentication** - Secure login and personalized experiences
- 🔹 **Mobile-Friendly UI** - Enhanced responsive design for mobile devices
- 🔹 **Multi-Language Support** - Interface localization
- 🔹 **Exportable Lists** - PDF/CSV export functionality
- 🔹 **Recipe Integration** - Connect grocery items to recipes
- 🔹 **Price Tracking** - Monitor and compare grocery prices
- 🔹 **Shopping List Sharing** - Collaborative grocery planning

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## ⭐ Show Your Support

Give a ⭐️ if this project helped you!

---

**Made with ❤️ by Mohomed Nasheeth**
