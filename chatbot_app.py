import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
from openai import OpenAI

# ---------------------
# 🔐 Load OpenAI Client
# ---------------------
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ---------------------
# 📂 Load Data
# ---------------------
@st.cache_data
def load_data():
    file_path = "C:\\Users\\htouray\\cleaned_lead_generation.csv"
    return pd.read_csv(file_path)

df = load_data()

st.set_page_config(page_title="Summa Support", page_icon="🔧", layout="centered")

st.title("🔧 Service Support Chatbot")

# ---------------------
# 🔎 Serial Number Search
# ---------------------
serial = st.text_input("🔍 Hello Valuable Customer, Please Enter Machine Serial Number:")

if serial:
    match = df[df["serial_number"].astype(str).str.strip() == serial.strip()]

    if not match.empty:
        customer = match.iloc[0]

        # Warranty calculation
        try:
            Creat_Date = pd.to_datetime(customer["date_sold"])
            warranty_end = Creat_Date + timedelta(days=2 * 365)
            warranty_status = "✅ Under Warranty" if datetime.now() <= warranty_end else "❌ Warranty Expired"
        except Exception:
            Creat_Date = "Unknown"
            warranty_end = "Unknown"
            warranty_status = "⚠️ Missing or invalid 'date_sold'"

        # Customer info display
        st.success("🔍 Serial number found!")
        st.markdown(f"""
        **Customer Name:** {customer['first_name']} {customer['last_name']}  
        **Company:** {customer['company_name']}  
        **Email:** {customer['email']}  
        **Phone:** {customer['phone_number']}  
        **Product:** {customer['product_interest']}  
        **Date Sold:** {Creat_Date}  
        **Warranty Ends:** {warranty_end}  
        **Warranty Status:** {warranty_status}  
        """)

        # ---------------------
        # 🛠 Troubleshooting Tips
        # ---------------------
        st.subheader("🛠 Troubleshooting Suggestions")
        product = str(customer["product_interest"]).lower()

        if "printer" in product:
            st.info("🧾 **Printer Tips:**\n- Check ink levels\n- Clean print head\n- Verify driver installation")
        elif "cutter" in product:
            st.info("🔪 **Cutter Tips:**\n- Inspect blades\n- Run calibration\n- Confirm correct media settings")
        else:
            st.warning("ℹ️ No troubleshooting guide found for this product type.")

        # ---------------------
        # 📷 Upload Photo
        # ---------------------
        st.subheader("📷 Upload Image of Issue (optional)")
        uploaded_img = st.file_uploader("Attach photo of the issue", type=["jpg", "jpeg", "png"])

        # ---------------------
        # 📝 Submit Service Request
        # ---------------------
        st.subheader("📝 Submit Service Request")
        issue = st.text_area("Describe the issue")
        contact_email = st.text_input("Confirm your email", value=customer["email"])

        if st.button("📨 Submit Request"):
            st.success("✅ Request submitted. Our team will contact you shortly.")

            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Service Request Summary", ln=True, align='C')
            pdf.ln(10)
            pdf.multi_cell(0, 10, txt=f"""
Customer: {customer['first_name']} {customer['last_name']}
Company: {customer['company_name']}
Email: {contact_email}
Phone: {customer['phone_number']}
Product: {customer['product_interest']}
Date Sold: {Creat_Date}
Warranty Ends: {warranty_end}
Warranty Status: {warranty_status}
Issue Description: {issue}
            """)
            pdf_path = f"service_request_{serial}.pdf"
            pdf.output(pdf_path)

            with open(pdf_path, "rb") as f:
                st.download_button("📥 Download Request Summary (PDF)", f, file_name=pdf_path)

            os.remove(pdf_path)
    else:
        st.error("❌ Serial number not found.")

# ---------------------
# 💬 Live Chat Assistant
# ---------------------
st.subheader("💬 Live Chat with Darrell Summa")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Chat input box (this comes first to capture input)
query = st.chat_input("Ask a question about your machine, warranty, or service...")

# Process the message before rendering
if query:
    st.session_state.messages.append({"content": query, "is_user": True})

    # OpenAI API call using latest client
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are Darrel Summa, a helpful customer service assistant specialized in machine support."},
            {"role": "user", "content": query}
        ]
    )

    reply = response.choices[0].message.content.strip()
    st.session_state.messages.append({"content": reply, "is_user": False})

# Display message bubbles AFTER messages are updated
for msg in st.session_state.messages:
    if msg["is_user"]:
        st.markdown(f"""
        <div style='text-align: right; background-color: #DCF8C6; padding: 8px 12px; border-radius: 15px; margin: 5px 0 5px auto; max-width: 75%;'>
        <strong>You:</strong><br>{msg["content"]}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style='text-align: left; background-color: #F1F0F0; padding: 8px 12px; border-radius: 15px; margin: 5px auto 5px 0; max-width: 75%;'>
        <strong>Darrell Summa:</strong><br>{msg["content"]}
        </div>
        """, unsafe_allow_html=True)
