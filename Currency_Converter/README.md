CURRENCY CONVERTER
==================

A simple Python command-line app that converts one currency into another using live exchange rates 
from exchangerate.host (with a fallback to Frankfurter API).

------------------------------------------------------------
FEATURES
------------------------------------------------------------
- Fetches live exchange rates from a free API
- Converts between any two currencies (e.g., USD → EUR, EUR → KZT)
- Automatically switches to a backup API if the main one is unavailable
- Simple command-line interface
- Written in pure Python, no frameworks required

------------------------------------------------------------
PROJECT STRUCTURE
------------------------------------------------------------
currency_converter/
│
├── main.py
├── requirements.txt
└── README.txt

------------------------------------------------------------
INSTALLATION
------------------------------------------------------------
1. Clone the repository or download the files:
   git clone https://github.com/yourusername/currency_converter.git
   cd currency_converter

2. Create and activate a virtual environment:
   python -m venv .venv

   For Windows:
   .venv\Scripts\activate

   For Mac/Linux:
   source .venv/bin/activate

3. Install dependencies:
   pip install -r requirements.txt

------------------------------------------------------------
USAGE
------------------------------------------------------------
Run the converter:
   python main.py

Then follow the prompts:

   === Currency Converter ===
   From currency (e.g., USD): usd
   To currency (e.g., EUR): eur
   Amount: 100

Example output:
   Rate: 1 USD = 0.9250 EUR
   100 USD = 92.50 EUR

------------------------------------------------------------
REQUIREMENTS
------------------------------------------------------------
requests==2.32.3

------------------------------------------------------------
API SOURCES
------------------------------------------------------------
- exchangerate.host
- frankfurter.app

------------------------------------------------------------
POSSIBLE IMPROVEMENTS
------------------------------------------------------------
- Add a Flask web interface
- Show available currency codes
- Display historical exchange rate charts
- Cache API responses locally

------------------------------------------------------------
LICENSE
------------------------------------------------------------
This project is open-source and free to use for educational and personal purposes.