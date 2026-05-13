# 💼 AI-Powered Expense Audit System

## 📌 Overview
This project is an AI-powered system that automates expense claim validation using OCR and intelligent decision-making. It extracts data from receipts and evaluates claims against company policies using rule-based logic and Retrieval-Augmented Generation (RAG).

It also includes a Human-in-the-Loop system where auditors can review and override AI decisions.

---

## 🚀 Features

- 📄 OCR-based receipt processing (Tesseract + EasyOCR fallback)
- 🧠 Intelligent data extraction (merchant, amount, date, currency)
- 📊 Policy validation using RAG (semantic search on policy documents)
- ⚠️ Detection of prohibited expenses (e.g., alcohol)
- 📅 Date validation between receipt and claim
- 👨‍💼 Auditor dashboard with override capability
- 💾 Claim storage with tracking and notifications

---

## 🧩 System Flow
User Upload → OCR → Data Extraction → Validation → Policy Retrieval (RAG) → Decision → Storage → UI

---

## 🛠️ Tech Stack

- **Language:** Python  
- **Backend:** Flask  
- **Frontend:** Streamlit  
- **OCR:** Tesseract, EasyOCR  
- **PDF Processing:** PyPDF2, pdf2image  
- **RAG:** FAISS + embeddings  
- **Storage:** JSON  

---

## 📂 Project Structure

ai-expense-audit-system/
│
├── app.py # Flask backend
├── ui.py # Streamlit frontend
├── main.py # Core processing pipeline
├── extractor.py # Data extraction logic
├── ocr.py # OCR handling
├── rag.py # Policy retrieval
├── storage.py # Claim storage
│
|── samples/ # Sample receipts
│
├── policy.pdf # Policy document
├── claims.json # Stored claims

---

## ▶️ How to Run
Make sure Python and pip are installed on your system.

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Start backend
```bash
python app.py
```
### 3. Start UI
```
streamlit run ui.py
```


