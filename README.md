# 🏞 Land Valuation Platform

A full-stack platform for determining land prices in Kenya using geospatial data and machine learning.
Kenya lacks any digital infrastructure by the government to accurately determine the price of land. That's why I created #'Arthi Kenya'#
This platform will work with banks, governments and individual businesses to make accurate price determination.

---

## 📦 Tech Stack

- *Backend*: Python + Flask  
- *Machine Learning*: Pandas, Scikit-learn  
- *Database*: PostgreSQL + PostGIS  
- *Frontend*: HTML, JavaScript  
- *Deployment*: Docker + Docker Compose  

---

## 📁 Project Structure

land-valuation-platform/
├── backend/              # Flask API
├── ML/                   # Model training and predictions
├── frontend/             # UI files
├── database/             # SQL scripts, sample data
├── Dockerfile            # App container
├── docker-compose.yml    # Service definitions
├── .env                  # Environment variables (ignored)
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation

---

## ⚙ Setup Instructions

### 1. Clone the repo
```bash
git clone https://github.com/kerrei/Landvaluation.git
cd Landvaluation
```

### 2. Add .env file
```
DB_HOST=db
DB_PORT=5432
DB_NAME=land_valuation
DB_USER=admin
DB_PASS=password
FLASK_APP=backend/app.py
FLASK_RUN_HOST=0.0.0.0
FLASK_RUN_PORT=5000
```

### 3. Run with Docker
```
docker-compose up --build
```

---

🚀 Usage
- Send POST requests to /predict with coordinates
- Visualize or edit data via frontend or DBeaver/pgAdmin
- Train or retrain ML model in ML/

---

👤 Author

Kerre – github.com/kerrei
