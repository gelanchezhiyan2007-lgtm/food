import os
import requests
import datetime
import streamlit as st
from PIL import Image
from utils.formatters import format_docx, format_pdf, format_html_preview
from utils.text_sanitizer import sanitize_text
from ai_core.gemini_generator import GeminiDocumentGenerator
import database

# Page Configuration
st.set_page_config(
    page_title="LegalEase | AI Legal Document Generator Studio",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS Styling for Modern Premium Look
st.markdown("""
<style>
    /* Main Theme Overrides */
    .stApp {
        background-color: #0b0f19;
        color: #f1f5f9;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    
    /* Header Container */
    .header-container {
        text-align: center;
        padding: 1.8rem 1rem 1rem 1rem;
        background: linear-gradient(180deg, rgba(30, 41, 59, 0.6) 0%, rgba(11, 15, 25, 0.9) 100%);
        border-bottom: 1px solid #1e293b;
        border-radius: 16px;
        margin-bottom: 1.5rem;
    }
    
    .header-title {
        background: linear-gradient(135deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.4rem;
        font-weight: 800;
        letter-spacing: -0.025em;
        margin-top: 0.5rem;
    }
    
    .header-subtitle {
        color: #94a3b8;
        font-size: 1.05rem;
        max-width: 650px;
        margin: 0.4rem auto 0 auto;
    }

    /* System Badge */
    .status-badge {
        display: inline-block;
        background: rgba(16, 185, 129, 0.15);
        color: #10b981;
        border: 1px solid rgba(16, 185, 129, 0.3);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-top: 10px;
    }

    /* Buttons & Cards */
    .stButton>button {
        background: linear-gradient(135deg, #4f46e5 0%, #3b82f6 100%);
        color: white;
        font-weight: 600;
        border-radius: 10px;
        padding: 0.6rem 1.4rem;
        border: none;
        transition: all 0.3s ease;
        box-shadow: 0 4px 14px rgba(79, 70, 229, 0.35);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(79, 70, 229, 0.5);
    }

    /* Input Field Labels */
    .stTextInput>label, .stTextArea>label, .stSelectbox>label {
        color: #e2e8f0 !important;
        font-weight: 600 !important;
    }

    /* Footer styling */
    .footer-text {
        text-align: center;
        padding: 2rem 0;
        color: #64748b;
        font-size: 0.85rem;
        border-top: 1px solid #1e293b;
        margin-top: 3rem;
    }
</style>
""", unsafe_allow_html=True)

# Helper Path Constants
LOGO_PATH = os.path.join(os.path.dirname(__file__), "assets", "legalease_logo.png")
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

# Session State Initialization
if "generated_doc" not in st.session_state:
    st.session_state.generated_doc = ""
if "doc_id" not in st.session_state:
    st.session_state.doc_id = None
if "doc_type" not in st.session_state:
    st.session_state.doc_type = "Employment Contract"
if "parties" not in st.session_state:
    st.session_state.parties = "TechNova Inc. (Employer), Jane Doe (Employee)"
if "terms" not in st.session_state:
    st.session_state.terms = "Annual compensation of $120,000 paid bi-weekly; 15 days paid leave per calendar year; Employee agrees to standard confidentiality and IP assignment; 12-month post-employment non-solicitation clause"
if "effective_date" not in st.session_state:
    st.session_state.effective_date = datetime.date.today().strftime("%B %d, %Y")
if "custom_instructions" not in st.session_state:
    st.session_state.custom_instructions = ""

# Check Backend API Health
backend_online = False
try:
    health_resp = requests.get(f"{BACKEND_URL}/", timeout=2)
    if health_resp.status_code == 200:
        backend_online = True
except Exception:
    backend_online = False

# Header Layout with Centered Logo
col_l1, col_l2, col_l3 = st.columns([1, 1.2, 1])
with col_l2:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, use_container_width=True)

status_text = "🟢 Connected: FastAPI Backend (127.0.0.1:8000) • SQLite DB Active" if backend_online else "🟡 Standalone Mode: Direct Engine Active"

st.markdown(f"""
<div class="header-container">
    <div class="header-title">LegalEase</div>
    <div class="header-subtitle">AI-Powered Legal Document Generator & Legal Tech Studio</div>
    <div class="status-badge">{status_text}</div>
</div>
""", unsafe_allow_html=True)

# Quick Preset Scenario Buttons
st.markdown("##### ⚡ Quick Load Use-Case Scenarios")
sc_col1, sc_col2, sc_col3 = st.columns(3)

with sc_col1:
    if st.button("🚀 Scenario 1: Startup Employment Contract", use_container_width=True):
        st.session_state.doc_type = "Employment Contract"
        st.session_state.parties = "TechNova Inc. (Employer), Jane Doe (Lead Software Engineer)"
        st.session_state.terms = "Annual base compensation of $135,000 paid bi-weekly; Stock options grant of 10,000 shares vesting over 4 years; 20 days paid leave per year; Full IP assignment to TechNova; 1-year non-compete within state lines"
        st.session_state.effective_date = "October 15, 2026"
        st.session_state.custom_instructions = "Include remote work allowance and annual performance review clause."
        st.rerun()

with sc_col2:
    if st.button("🛡️ Scenario 2: Freelance NDA", use_container_width=True):
        st.session_state.doc_type = "Non-Disclosure Agreement (NDA)"
        st.session_state.parties = "John Doe (Freelancer / Recipient), ABC Corp (Client / Disclosing Party)"
        st.session_state.terms = "Mutual confidentiality for source code and business strategy; Confidentiality obligations remain in effect for 3 years post-termination; Materials to be returned or destroyed within 10 days of request"
        st.session_state.effective_date = "October 01, 2026"
        st.session_state.custom_instructions = "Specify governing law as the State of Delaware."
        st.rerun()

with sc_col3:
    if st.button("🏠 Scenario 3: Residential Lease", use_container_width=True):
        st.session_state.doc_type = "Residential Lease Agreement"
        st.session_state.parties = "Alice Smith (Landlord / Lessor), XYZ Realty & Bob Johnson (Tenant / Lessee)"
        st.session_state.terms = "Property Address: 742 Evergreen Terrace, Springfield; Monthly Rent: $2,500 due on 1st of each month; Security Deposit: $2,500 refundable; Lease Term: 12 Months; No unauthorized pets permitted"
        st.session_state.effective_date = "November 01, 2026"
        st.session_state.custom_instructions = "Include landlord right to inspect property with 24 hours prior notice."
        st.rerun()

st.markdown("---")

# Sidebar for Database History
st.sidebar.markdown("### 📜 Database Saved History")
st.sidebar.caption("Stored contracts in SQLite (`legalease.db`)")

saved_docs = []
try:
    if backend_online:
        h_resp = requests.get(f"{BACKEND_URL}/history", timeout=3)
        if h_resp.status_code == 200:
            saved_docs = h_resp.json().get("documents", [])
    else:
        saved_docs = database.get_all_documents()
except Exception:
    saved_docs = database.get_all_documents()

if not saved_docs:
    st.sidebar.info("No saved documents in database yet. Generate a contract to see history here!")
else:
    for doc_item in saved_docs[:10]: # Show top 10 recent documents
        d_id = doc_item["id"]
        d_type = doc_item["document_type"]
        d_date = doc_item["created_at"]
        d_parties = doc_item["parties"]

        with st.sidebar.expander(f"📄 #{d_id}: {d_type}"):
            st.write(f"**Parties**: {d_parties}")
            st.caption(f"📅 Created: {d_date}")
            col_h1, col_h2 = st.columns(2)
            with col_h1:
                if st.button("Load 👁️", key=f"load_{d_id}", use_container_width=True):
                    st.session_state.generated_doc = doc_item["content"]
                    st.session_state.doc_id = d_id
                    st.session_state.doc_type = d_type
                    st.session_state.parties = d_parties
                    st.session_state.terms = doc_item.get("terms", "")
                    st.session_state.effective_date = doc_item.get("effective_date", "")
                    st.session_state.custom_instructions = doc_item.get("custom_instructions", "")
                    st.rerun()
            with col_h2:
                if st.button("Delete 🗑️", key=f"del_{d_id}", use_container_width=True):
                    if backend_online:
                        requests.delete(f"{BACKEND_URL}/history/{d_id}")
                    else:
                        database.delete_document_by_id(d_id)
                    st.rerun()

# Main Interface Layout
col_input, col_output = st.columns([1, 1.25], gap="large")

with col_input:
    st.markdown("### 📝 Document Configuration")

    doc_options = [
        "Employment Contract",
        "Non-Disclosure Agreement (NDA)",
        "Residential Lease Agreement",
        "Freelance Work Contract",
        "Employment Offer Letter",
        "Service Level Agreement (SLA)",
        "Custom Document Type"
    ]

    selected_type = st.selectbox(
        "1. Document Type",
        options=doc_options,
        index=doc_options.index(st.session_state.doc_type) if st.session_state.doc_type in doc_options else 0
    )

    if selected_type == "Custom Document Type":
        final_doc_type = st.text_input("Specify Custom Document Title", value="Custom Legal Agreement")
    else:
        final_doc_type = selected_type

    parties_input = st.text_area(
        "2. Parties Involved",
        value=st.session_state.parties,
        height=90,
        help="Specify full names and legal roles of involved entities."
    )

    terms_input = st.text_area(
        "3. Terms & Conditions (Use ';' to separate bullet points)",
        value=st.session_state.terms,
        height=130,
        help="Separate distinct clauses or stipulations using semicolons (;)."
    )

    effective_date_input = st.text_input(
        "4. Effective Date",
        value=st.session_state.effective_date
    )

    custom_instr_input = st.text_area(
        "5. Additional Custom Instructions (Optional)",
        value=st.session_state.custom_instructions,
        height=80,
        help="Provide any extra clauses or state jurisdiction requirements."
    )

    generate_btn = st.button("🚀 Generate & Save to Database", use_container_width=True)

    if generate_btn:
        st.session_state.doc_type = final_doc_type
        st.session_state.parties = parties_input
        st.session_state.terms = terms_input
        st.session_state.effective_date = effective_date_input
        st.session_state.custom_instructions = custom_instr_input

        with st.spinner("⚖️ Processing via FastAPI Backend & Gemini AI..."):
            generated_text = None
            new_id = None

            if backend_online:
                try:
                    payload = {
                        "document_type": final_doc_type,
                        "parties": parties_input,
                        "terms": terms_input,
                        "dates": effective_date_input,
                        "custom_instructions": custom_instr_input
                    }
                    resp = requests.post(f"{BACKEND_URL}/generate", json=payload, timeout=12)
                    if resp.status_code == 200:
                        data = resp.json()
                        generated_text = data.get("sanitized_content") or data.get("raw_content")
                        new_id = data.get("id")
                except Exception as e:
                    st.warning(f"Backend call error: {e}. Falling back to direct database engine.")

            if not generated_text:
                generator = GeminiDocumentGenerator()
                raw = generator.generate_document(
                    document_type=final_doc_type,
                    parties=parties_input,
                    terms=terms_input,
                    dates=effective_date_input,
                    custom_instructions=custom_instr_input
                )
                generated_text = sanitize_text(raw)
                new_id = database.save_document(
                    document_type=final_doc_type,
                    parties=parties_input,
                    terms=terms_input,
                    effective_date=effective_date_input,
                    custom_instructions=custom_instr_input,
                    content=generated_text
                )

            st.session_state.generated_doc = generated_text
            st.session_state.doc_id = new_id
            st.success(f"✨ Document Generated & Saved to Database (ID: #{new_id})!")
            st.rerun()

with col_output:
    st.markdown("### 📄 Document Studio & Export")

    if not st.session_state.generated_doc:
        st.info("👈 Fill in configuration details on the left and click **'Generate & Save to Database'** to create your contract.")
    else:
        if st.session_state.doc_id:
            st.caption(f"💾 Active Record ID: #{st.session_state.doc_id} | Stored in SQLite DB (`legalease.db`)")

        tab_preview, tab_edit, tab_export = st.tabs(["👁️ Styled Preview", "✏️ Edit Document", "📥 Download & Export"])

        with tab_preview:
            preview_html = format_html_preview(st.session_state.generated_doc, doc_type=st.session_state.doc_type)
            st.markdown(preview_html, unsafe_allow_html=True)

        with tab_edit:
            st.markdown("##### Modify wording or custom clauses in real-time:")
            edited_text = st.text_area(
                "Live Document Editor",
                value=st.session_state.generated_doc,
                height=450,
                key="doc_editor_area"
            )
            if edited_text != st.session_state.generated_doc:
                st.session_state.generated_doc = edited_text
                st.caption("✔️ Document changes saved locally for instant export!")

        with tab_export:
            st.markdown("##### Select Export Format")
            st.markdown("Download branded, ready-to-use documents complete with custom logo, terms tables, headers, and legal footers.")

            exp_col1, exp_col2, exp_col3 = st.columns(3)

            filename_base = st.session_state.doc_type.lower().replace(" ", "_").replace("(", "").replace(")", "")

            with exp_col1:
                st.markdown("#### 📄 Plain Text")
                st.caption("Clean unformatted .txt draft.")
                st.download_button(
                    label="Download .TXT",
                    data=st.session_state.generated_doc.encode("utf-8"),
                    file_name=f"{filename_base}.txt",
                    mime="text/plain",
                    use_container_width=True
                )

            with exp_col2:
                st.markdown("#### 📝 Word (.DOCX)")
                st.caption("Includes Logo, Times New Roman, Terms Table & Footer.")
                docx_bytes = format_docx(
                    text=st.session_state.generated_doc,
                    doc_type=st.session_state.doc_type,
                    logo_path=LOGO_PATH if os.path.exists(LOGO_PATH) else None,
                    terms_str=st.session_state.terms
                )
                st.download_button(
                    label="Download .DOCX",
                    data=docx_bytes,
                    file_name=f"{filename_base}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )

            with exp_col3:
                st.markdown("#### 📕 PDF Document")
                st.caption("Branded PDF with Headers, Footers & Logo.")
                pdf_bytes = format_pdf(
                    text=st.session_state.generated_doc,
                    doc_type=st.session_state.doc_type,
                    logo_path=LOGO_PATH if os.path.exists(LOGO_PATH) else None,
                    terms_str=st.session_state.terms
                )
                st.download_button(
                    label="Download .PDF",
                    data=pdf_bytes,
                    file_name=f"{filename_base}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

# Application Footer
st.markdown("""
<div class="footer-text">
    LegalEase SaaS • FastAPI Backend API • SQLite Database Persistence • Google Gemini 1.5 Pro AI
</div>
""", unsafe_allow_html=True)
