# 🏦 Automated Personal Loan Document Processing Background

A Streamlit app that automates the extraction and validation of key information from scanned personal loan application documents using OCR.

---

## 🚀 Features

- 🖼️ Image preprocessing for enhanced OCR accuracy  
- 🔍 OCR text extraction using Tesseract  
- 📄 Field parsing using regular expressions (Name, Address, Income, Loan Amount)  
- ✅ Data validation logic:
  - Income ≥ $10,000
  - Loan Amount ≥ $1,000  
- ✍️ Manual correction interface for OCR errors  
- 📤 Simulated bank system integration for submission  

---

## 📄 Input Format

The input is an image (JPG/PNG) of a filled loan application.  
Example text extracted via OCR:

Name: John Doe  
Address: New Delhi   
Annual Income: $25,000   
Loan Amount: $5,000  

---

## ✅ Data Validation Rules

| Field        | Validation Rule                 |
|--------------|----------------------------------|
| Name         | Must contain at least 2 words    |
| Address      | Must not be empty                |
| Income       | Must be ≥ $10,000                |
| Loan Amount  | Must be ≥ $1,000                 |

❗ Fields that fail validation will be excluded from final output, and a warning will be displayed in the app.

---

## 🤖 Sample Output

Extracted Fields:

Name: John Doe

Address: New Delhi

Income: 25000

Loan Amount: 5000

✅ Data successfully validated and submitted to the bank's loan processing system.


---


