
# 🚗 Drivio – Intelligent Car Valuation Engine

Drivio is an AI-powered used car valuation system that combines machine learning, explainable AI (SHAP), 
business-aware pricing logic, uncertainty estimation, and negotiation intelligence into a single interactive web application.

It is designed as a complete AI product — not just a model.

---

## 🌟 Key Features

### 💰 Machine Learning Price Prediction
- Trained regression model for used car valuation
- Encodes categorical + numerical features
- Real-time prediction via Streamlit UI

### 📊 Explainable AI (SHAP Integration)
- Feature contribution breakdown
- Positive vs negative price impact
- Transparent reasoning behind predictions

### 🧠 Business-Aware Ownership Adjustment
- Single Owner → Premium adjustment
- Second Owner → Moderate depreciation
- Multiple Owners → Higher resale risk discount
- Clear separation between ML prediction and business logic

### 📈 Uncertainty Range Estimation
- Displays price confidence interval
- Reflects real-world market variability
- Improves trust in predictions

### 🤝 Negotiation Intelligence
- Buyer strategy suggestions
- Seller pricing guidance
- Risk-aware negotiation insights

### 🎨 Enterprise-Level UI
- Gradient animated brand header
- Interactive SHAP feature charts
- Vehicle preview by brand & model
- Clean valuation breakdown cards
- Startup-style polished design

---

## 🏗️ System Architecture

Streamlit UI  
      ↓  
CarPriceAgent (Orchestrator)  
      ↓  
Predictor (ML Model)  
      ↓  
SHAP Explainability  
      ↓  
Ownership Adjustment Layer  
      ↓  
Negotiation Agent  

---

## 📦 Project Structure

drivio/  
│  
├── app/  
│   └── streamlit_app.py  
│  
├── src/  
│   ├── model/  
│   │   └── predictor.py  
│   │  
│   ├── agents/  
│   │   ├── price_agent.py  
│   │   └── negotiation_agent.py  
│   │  
│   └── explainability/  
│       └── shap_agent.py  
│  
├── artifacts/  
│   ├── xgb_car_price_model.pkl  
│   └── model_features.pkl  
│  
└── requirements.txt  

---

## 🧮 Input Features

- Brand  
- Model  
- Fuel Type  
- Transmission  
- Body Type  
- City  
- Number of Owners  
- Car Age  
- Log(KM Driven)  

---

## 🛠️ Tech Stack

- Python 3.12  
- Scikit-learn  
- XGBoost  
- SHAP  
- Pandas  
- Altair  
- Streamlit  
- Joblib  

---

## 🚀 How To Run Locally

1️⃣ Install Dependencies

pip install -r requirements.txt

2️⃣ Run Streamlit App

streamlit run app/streamlit_app.py

---

## 📊 Output Includes

- Final Estimated Price  
- Estimated Market Range (Uncertainty Interval)  
- SHAP Feature Impact Visualization  
- Ownership Adjustment Breakdown  
- AI Generated Market Summary  
- Buyer & Seller Negotiation Strategy  

---

## 🎯 What This Project Demonstrates

✔ Applied Machine Learning  
✔ Explainable AI (XAI)  
✔ Business Logic Integration  
✔ Modular AI System Design  
✔ Product Thinking  
✔ Interactive Deployment  

This project showcases end-to-end AI product engineering — from model training to explainable deployment.

---

## 🎯 Output Screenshot

1)User Input Interface

<img width="1910" height="927" alt="image" src="https://github.com/user-attachments/assets/ffd8a4ac-40b3-4650-b2f3-c540027fb56c" />




2)Valuation Interface




<img width="1897" height="916" alt="image" src="https://github.com/user-attachments/assets/0b37e588-69d0-400b-9d3a-69f0217f9143" />

<img width="1897" height="927" alt="image" src="https://github.com/user-attachments/assets/4ad9a007-d473-4014-8c53-6640d966cb0a" />

<img width="1901" height="920" alt="image" src="https://github.com/user-attachments/assets/4dc1cb71-7fad-4938-9964-036c93f538c9" />

<img width="1902" height="927" alt="image" src="https://github.com/user-attachments/assets/b7137641-8f7f-46f4-81cf-a2bdcd835c75" />

---

## 👨‍💻 Author

Aman Sharma  
Focused on building intelligent, explainable AI systems.
