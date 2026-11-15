
# Superstore Decision Support System (DSS)

## 1. Introduction

Superstore DSS is a decision support application
designed to monitor and evaluate sales performance
using the Superstore dataset.

## 2. Technologies

- Python 3.12
- SQL Server
- Streamlit
- Pandas
- SQLAlchemy
- PyODBC
- Plotly

## 3. Main Features

- Sales Overview
- Sales Trend Analysis
- Product Performance Analysis
- Regional Analysis
- Customer Analysis
- Decision Support

## 4. Database

The application connects to a SQL Server Data Warehouse
using a Star Schema architecture.

## 5. Installation

Clone the repository:

```bash
git clone https://github.com/your-username/Superstore-DSS.git
```

Create and activate virtual environment:

```bash
python -m venv venv
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
streamlit run app.py
```

## 6. Requirements

- Python 3.12
- SQL Server
- ODBC Driver 17 for SQL Server
- Superstore_DW database
