import streamlit as st
import numpy as np
import pytesseract
import re
from PIL import Image, ImageEnhance, ImageFilter
from io import BytesIO
from datetime import datetime

# Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# ========== Class Definition ==========

class LoanDocProcessor:
    def __init__(self):
        self.field_templates = {
            'name': {
                'patterns': [r"Applicant\s*[:\-\s]+(.+)", r"Full\s*Name\s*[:\-\s]+(.+)", r"NAME\s*[:\-\s]+(.+)"],
                'validator': lambda x: len(x.split()) >= 2
            },
            'address': {
                'patterns': [r"Address\s*[:\-\s]+(.+)", r"Residential\s*Address\s*[:\-\s]+(.+)"],
                'validator': lambda x: len(x.strip()) > 0
            },
            'income': {
                'patterns': [r"Income\s*Details\s*[:\-\s]*₹?\$?([\d,]+)", r"Annual\s*Income\s*[:\-\s]*₹?\$?([\d,]+)"],
                'validator': lambda x: float(x.replace(',', '')) >= 10000
            },
            'loan_amount': {
                'patterns': [r"Loan\s*Amount\s*[:\-\s]*₹?\$?([\d,]+)", r"Amount\s*Requested\s*[:\-\s]*₹?\$?([\d,]+)"],
                'validator': lambda x: float(x.replace(',', '')) > 1000
            }
        }

    def preprocess_image(self, image_data):
        img = Image.open(image_data).convert('L')
        img = img.filter(ImageFilter.MedianFilter())
        img = ImageEnhance.Contrast(img).enhance(2)
        img = img.point(lambda x: 0 if x < 140 else 255)
        return np.array(img)

    def extract_text(self, img):
        config = r'--oem 3 --psm 6'
        return pytesseract.image_to_string(img, config=config)

    def extract_fields(self, text):
        results = {}
        for field, config in self.field_templates.items():
            results[field] = {'matches': [], 'final_value': None}
            for pattern in config['patterns']:
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    val = match.group(1).strip(": -'\"")
                    valid = False
                    try:
                        valid = config['validator'](val)
                    except:
                        pass
                    results[field]['matches'].append({
                        'value': val,
                        'valid': valid,
                        'confidence': 'high' if '₹' in val or '$' in val else 'medium'
                    })
                    # Take only the first valid match for each field
                    if valid and results[field]['final_value'] is None:
                        results[field]['final_value'] = val
        return results

    def download_summary(self, data):
        buffer = BytesIO()
        content = "\n".join([f"{k.title().replace('_', ' ')}: {v}" for k, v in data.items()])
        buffer.write(content.encode())
        buffer.seek(0)
        return buffer
    
    def send_to_bank_system(self, data):
        st.success("✅ Data successfully validated and submitted to the bank's loan processing system.")
        st.markdown("### 📤 Submitted Data")
        for k, v in data.items():
            st.write(f"**{k.replace('_', ' ').title()}**: {v}")

# ========== Streamlit App ==========

st.set_page_config(page_title="🏦 2. Problem Statement: Automated Personal Loan Document Processing ", layout="wide")
st.markdown("<h1 style='text-align: center;'>🏦 2. Problem Statement: Automated Personal Loan Document Processing </h1>", unsafe_allow_html=True)
st.caption("An intelligent, OCR-powered system for loan document verification & extraction.")

uploaded_file = st.file_uploader("📂 Upload Loan Application", type=["png", "jpg", "jpeg"])

if uploaded_file:
    processor = LoanDocProcessor()
    img = processor.preprocess_image(uploaded_file)
    st.image(img, caption="📸 Preprocessed Image", use_container_width=True)

    raw_text = processor.extract_text(img)
    st.subheader("📝 OCR Text (editable)")
    user_text = st.text_area("Review & Correct OCR output if needed:", value=raw_text, height=250)

    extracted = processor.extract_fields(user_text)

    st.subheader("🔍 Field Extraction & Validation")
    user_inputs = {}
    col1, col2 = st.columns(2)

    # Field Inputs Section
    with col1:
        for field, info in extracted.items():
            val = info['final_value'] or ""
            user_val = st.text_input(f"{field.replace('_', ' ').title()} 🧾", value=val)
            user_inputs[field] = user_val

    # Field Validation Summary Section (Updated to show field name only once and avoid duplicate values)
    with col2:
        st.markdown("### 🧠 Field Validation Summary")
        for field, info in extracted.items():
            # Display the field name only once
            st.markdown(f"**{field.replace('_', ' ').title()}**:")
            
            # Display only the first valid match
            if info['final_value']:
                color = "green" if info['matches'][0]['valid'] else "red"
                symbol = "✅" if info['matches'][0]['valid'] else "❌"
                st.markdown(f"- `{info['final_value']}` <span style='color:{color}'>{symbol} ({info['matches'][0]['confidence']})</span>", unsafe_allow_html=True)

    if st.button("🚀 Submit to Bank System"):
        processor.send_to_bank_system(user_inputs)
        st.balloons()
        st.download_button("📥 Download Submission Summary", data=processor.download_summary(user_inputs),
                           file_name=f"Loan_Submission_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
