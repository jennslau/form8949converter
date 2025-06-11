import streamlit as st
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
import io
import zipfile
from datetime import datetime
import re
import requests
import PyPDF2
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def main():
    """Main Streamlit application for Form 8949 generation"""
    st.set_page_config(
        page_title="Professional Form 8949 Generator",
        page_icon="📋",
        layout="wide"
    )
    
    # Professional styling
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        border-radius: 10px;
        padding: 2rem;
        margin-bottom: 2rem;
        text-align: center;
    }
    .section-header {
        color: #1e3c72;
        border-bottom: 2px solid #2a5298;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .instruction-box {
        background-color: #f8f9fa;
        border-left: 4px solid #2a5298;
        padding: 1rem;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>📋 Professional Form 8949 Generator</h1>
        <p>Convert your cryptocurrency transactions to official IRS Form 8949</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Instructions
    with st.expander("📖 Instructions & Requirements", expanded=False):
        st.markdown("""
        ### Required CSV Columns:
        - **Description**: Asset description (e.g., "BTC cryptocurrency")
        - **Date Acquired**: Purchase date (MM/DD/YYYY)
        - **Date Sold**: Sale date (MM/DD/YYYY)
        - **Proceeds**: Sale amount (column d)
        - **Cost Basis**: Purchase cost (column e)
        - **Gain/Loss**: Calculated gain or loss (column h)
        
        ### Features:
        - ✅ Maps directly to official IRS Form 8949 fields
        - ✅ Automatically handles multiple pages (14 transactions per page)
        - ✅ Separates short-term and long-term transactions
        - ✅ Applies taxpayer information to all pages
        - ✅ Professional PDF output ready for IRS submission
        """)
    
    # Taxpayer Information Section
    st.markdown('<h2 class="section-header">👤 Taxpayer Information</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        taxpayer_name = st.text_input(
            "Full Name (as shown on tax return)",
            placeholder="John and Jane Smith"
        )
    with col2:
        taxpayer_ssn = st.text_input(
            "Social Security Number",
            placeholder="123-45-6789"
        )
    
    # Form Configuration
    st.markdown('<h2 class="section-header">⚙️ Form Configuration</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        tax_year = st.selectbox(
            "Tax Year",
            [2024, 2023, 2022, 2021, 2020],
            index=0
        )
    
    with col2:
        default_box_type = st.selectbox(
            "Default Box Type",
            [
                "Box B - Basis NOT reported to IRS",
                "Box A - Basis reported to IRS", 
                "Box C - Various situations"
            ],
            index=0
        )
    
    # File Upload Section
    st.markdown('<h2 class="section-header">📁 Upload Transaction Data</h2>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Choose CSV file with your cryptocurrency transactions",
        type=['csv'],
        help="Upload a CSV file with your transaction data"
    )
    
    if uploaded_file is not None:
        try:
            # Read and validate CSV
            df = pd.read_csv(uploaded_file)
            st.success(f"✅ File uploaded successfully! Found {len(df)} transactions.")
            
            # Display preview
            with st.expander("📊 Data Preview", expanded=True):
                st.dataframe(df.head(10))
            
            # Validate required columns
            required_columns = ['Description', 'Date Acquired', 'Date Sold', 'Proceeds', 'Cost Basis', 'Gain/Loss']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                st.error(f"❌ Missing required columns: {', '.join(missing_columns)}")
                st.info("Please ensure your CSV has all required columns with exact names.")
                return
            
            # Process transactions
            transactions = process_transactions(df)
            
            if not transactions:
                st.error("❌ No valid transactions found in the uploaded file.")
                return
            
            # Separate short-term and long-term
            short_term, long_term = separate_transactions_by_term(transactions)
            
            # Display summary
            st.markdown('<h2 class="section-header">📈 Transaction Summary</h2>', unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Transactions", len(transactions))
            with col2:
                st.metric("Short-term", len(short_term))
            with col3:
                st.metric("Long-term", len(long_term))
            with col4:
                total_gain_loss = sum(t['gain_loss'] for t in transactions)
                st.metric("Net Gain/Loss", f"${total_gain_loss:,.2f}")
            
            # Generate Forms
            if st.button("🚀 Generate Form 8949 PDFs", type="primary"):
                if not taxpayer_name or not taxpayer_ssn:
                    st.error("⚠️ Please enter taxpayer name and SSN before generating forms.")
                    return
                
                with st.spinner("Generating professional Form 8949 PDFs..."):
                    pdf_files = generate_all_forms(
                        short_term, 
                        long_term, 
                        taxpayer_name, 
                        taxpayer_ssn, 
                        tax_year, 
                        default_box_type
                    )
                
                if pdf_files:
                    if len(pdf_files) == 1:
                        # Single PDF download
                        st.download_button(
                            label="📥 Download Form 8949",
                            data=pdf_files[0]['content'],
                            file_name=pdf_files[0]['filename'],
                            mime="application/pdf"
                        )
                    else:
                        # Multiple PDFs in ZIP
                        zip_data = create_zip_file(pdf_files)
                        st.download_button(
                            label="📦 Download All Forms (ZIP)",
                            data=zip_data,
                            file_name=f"Form_8949_{tax_year}_Complete.zip",
                            mime="application/zip"
                        )
                    
                    st.success(f"✅ Generated {len(pdf_files)} Form 8949 PDF(s) successfully!")
                else:
                    st.error("❌ Failed to generate PDF files. Please check your data and try again.")
        
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")

def process_transactions(df):
    """Process CSV data into standardized transaction format"""
    transactions = []
    
    for _, row in df.iterrows():
        try:
            # Parse dates
            date_acquired = pd.to_datetime(row['Date Acquired'])
            date_sold = pd.to_datetime(row['Date Sold'])
            
            # Calculate holding period
            holding_days = (date_sold - date_acquired).days
            is_short_term = holding_days <= 365
            
            # Clean monetary values
            proceeds = clean_currency_value(row['Proceeds'])
            cost_basis = clean_currency_value(row['Cost Basis'])
            gain_loss = clean_currency_value(row['Gain/Loss'])
            
            # Create transaction record
            transaction = {
                'description': str(row['Description']).strip(),
                'date_acquired': date_acquired,
                'date_sold': date_sold,
                'proceeds': proceeds,
                'cost_basis': cost_basis,
                'gain_loss': gain_loss,
                'is_short_term': is_short_term,
                'holding_days': holding_days
            }
            
            transactions.append(transaction)
            
        except Exception as e:
            st.warning(f"⚠️ Skipping invalid row: {e}")
            continue
    
    return transactions

def clean_currency_value(value):
    """Clean and parse currency values from various formats"""
    if pd.isna(value) or value == '' or value == '-':
        return 0.0
    
    # Convert to string and clean
    str_val = str(value).strip()
    
    # Handle parentheses for negative values
    is_negative = False
    if '(' in str_val and ')' in str_val:
        is_negative = True
        str_val = str_val.replace('(', '').replace(')', '')
    
    # Remove currency symbols, commas, and spaces
    str_val = re.sub(r'[,$\s]', '', str_val)
    
    try:
        result = float(str_val)
        return -result if is_negative else result
    except:
        return 0.0

def separate_transactions_by_term(transactions):
    """Separate transactions into short-term and long-term based on holding period"""
    short_term = [t for t in transactions if t['is_short_term']]
    long_term = [t for t in transactions if not t['is_short_term']]
    return short_term, long_term

def generate_all_forms(short_term, long_term, taxpayer_name, taxpayer_ssn, tax_year, default_box_type):
    """Generate all required Form 8949 PDFs"""
    pdf_files = []
    
    # Generate short-term forms (Part I)
    if short_term:
        short_term_pdfs = generate_form_8949_pages(
            short_term,
            "Part I",
            taxpayer_name,
            taxpayer_ssn,
            tax_year,
            default_box_type,
            "Short_Term"
        )
        pdf_files.extend(short_term_pdfs)
    
    # Generate long-term forms (Part II)
    if long_term:
        long_term_pdfs = generate_form_8949_pages(
            long_term,
            "Part II",
            taxpayer_name,
            taxpayer_ssn,
            tax_year,
            default_box_type,
            "Long_Term"
        )
        pdf_files.extend(long_term_pdfs)
    
    return pdf_files

def generate_form_8949_pages(transactions, part_type, taxpayer_name, taxpayer_ssn, tax_year, box_type, term_suffix):
    """Generate Form 8949 pages for a set of transactions"""
    pdf_files = []
    
    # Split transactions into pages (14 per page maximum)
    transactions_per_page = 14
    total_pages = (len(transactions) + transactions_per_page - 1) // transactions_per_page
    
    for page_num in range(total_pages):
        start_idx = page_num * transactions_per_page
        end_idx = min(start_idx + transactions_per_page, len(transactions))
        page_transactions = transactions[start_idx:end_idx]
        
        # Create PDF for this page
        buffer = io.BytesIO()
        
        # Try official template first, fallback to custom if needed
        success = create_form_with_official_template(
            buffer, page_transactions, part_type, taxpayer_name, 
            taxpayer_ssn, tax_year, box_type, page_num + 1, total_pages, transactions
        )
        
        if not success:
            create_custom_form_8949(
                buffer, page_transactions, part_type, taxpayer_name,
                taxpayer_ssn, tax_year, box_type, page_num + 1, total_pages, transactions
            )
        
        # Generate filename
        if total_pages == 1:
            filename = f"Form_8949_{tax_year}_{term_suffix}_{taxpayer_name.replace(' ', '_')}.pdf"
        else:
            filename = f"Form_8949_{tax_year}_{term_suffix}_Page_{page_num + 1}_{taxpayer_name.replace(' ', '_')}.pdf"
        
        pdf_files.append({
            'filename': filename,
            'content': buffer.getvalue()
        })
    
    return pdf_files

def create_form_with_official_template(buffer, transactions, part_type, taxpayer_name, taxpayer_ssn, tax_year, box_type, page_num, total_pages, all_transactions):
    """Create Form 8949 using official IRS template with PERFECT alignment to form table structure"""
    try:
        # Get official IRS Form 8949 PDF
        official_pdf = get_official_form_8949(tax_year)
        if not official_pdf:
            return False
        
        # Read the official PDF
        official_pdf_stream = io.BytesIO(official_pdf)
        pdf_reader = PyPDF2.PdfReader(official_pdf_stream)
        
        # Select appropriate page (Part I = page 1, Part II = page 2)
        template_page_num = 0 if part_type == "Part I" else 1
        if template_page_num >= len(pdf_reader.pages):
            template_page_num = 0
        
        template_page = pdf_reader.pages[template_page_num]
        
        # Create overlay with transaction data
        overlay_buffer = io.BytesIO()
        c = canvas.Canvas(overlay_buffer, pagesize=letter)
        width, height = letter
        
        # PRECISELY MEASURED COORDINATES - Based on actual IRS Form 8949 structure
        
        # Taxpayer information fields (header boxes) - CORRECTED POSITIONING
        name_field_x = 75       # Left edge of name field box
        name_field_y = height - 155
        ssn_field_x = 550       # Right-aligned in SSN field box  
        ssn_field_y = height - 155
        
        # Checkbox positions - measured from actual form
        if part_type == "Part I":
            checkbox_base_y = height - 427   # Part I checkboxes (A, B, C)
            # CRITICAL FIX: Move table start DOWN to actual first data row
            table_start_y = height - 595     # First transaction row (after headers)
        else:
            checkbox_base_y = height - 350   # Part II checkboxes (D, E, F) 
            table_start_y = height - 595     # Same position for Part II
        
        checkbox_x = 45
        
        # RECALIBRATED column positions - measured to fit within exact form boundaries
        col_positions = {
            'description': 50,      # Column (a) - fits within narrow left column
            'date_acquired': 195,   # Column (b) - centered in date column
            'date_sold': 260,       # Column (c) - centered in date column
            'proceeds': 340,        # Column (d) - right-aligned within proceeds column
            'cost_basis': 415,      # Column (e) - right-aligned within basis column  
            'code': 455,            # Column (f) - centered in code column
            'adjustment': 495,      # Column (g) - right-aligned in adjustment column
            'gain_loss': 565        # Column (h) - right-aligned in gain/loss column
        }
        
        # INCREASED row spacing to match actual form row height
        row_height = 19.5  # Measured spacing between form table rows
        
        # Fill taxpayer information with corrected positioning
        c.setFont("Helvetica", 10)
        c.drawString(name_field_x, name_field_y, taxpayer_name[:40])
        c.drawRightString(ssn_field_x, ssn_field_y, taxpayer_ssn)
        
        # Check appropriate box
        c.setFont("Helvetica", 12)
        box_letter = box_type.split()[1]  # Extract A, B, or C
        
        if part_type == "Part I":
            if box_letter == "A":
                c.drawString(checkbox_x, checkbox_base_y, "✓")
            elif box_letter == "B": 
                c.drawString(checkbox_x, checkbox_base_y - 20, "✓")
            elif box_letter == "C":
                c.drawString(checkbox_x, checkbox_base_y - 40, "✓")
        else:  # Part II - maps A->D, B->E, C->F
            if box_letter == "A":  # Maps to Box D for long-term
                c.drawString(checkbox_x, checkbox_base_y, "✓")
            elif box_letter == "B":  # Maps to Box E for long-term
                c.drawString(checkbox_x, checkbox_base_y - 20, "✓")
            elif box_letter == "C":  # Maps to Box F for long-term
                c.drawString(checkbox_x, checkbox_base_y - 40, "✓")
        
        # REDUCED font size to fit cleanly within cells
        c.setFont("Helvetica", 5.5)  # Smaller font for clean cell fit
        
        # Fill transaction data with precise alignment and text width checking
        for i, transaction in enumerate(transactions[:14]):  # Maximum 14 transactions per page
            y_pos = table_start_y - (i * row_height)
            
            # Format and truncate data to fit within column boundaries
            description = transaction['description'][:20]  # Strict limit for narrow column
            date_acquired = transaction['date_acquired'].strftime('%m/%d/%Y')
            date_sold = transaction['date_sold'].strftime('%m/%d/%Y')
            
            # Column (a) - Description: Left-aligned, truncated to fit
            c.drawString(col_positions['description'], y_pos, description)
            
            # Column (b) - Date acquired: Centered precisely
            date_acq_width = c.stringWidth(date_acquired)
            c.drawString(col_positions['date_acquired'] - date_acq_width/2, y_pos, date_acquired)
            
            # Column (c) - Date sold: Centered precisely
            date_sold_width = c.stringWidth(date_sold)
            c.drawString(col_positions['date_sold'] - date_sold_width/2, y_pos, date_sold)
            
            # Column (d) - Proceeds: Right-aligned within column boundaries
            proceeds_text = f"{transaction['proceeds']:,.2f}"
            # Check width and truncate if necessary
            if c.stringWidth(proceeds_text) > 65:  # Column width limit
                proceeds_text = f"{transaction['proceeds']:,.0f}"
            c.drawRightString(col_positions['proceeds'], y_pos, proceeds_text)
            
            # Column (e) - Cost basis: Right-aligned within column boundaries
            basis_text = f"{transaction['cost_basis']:,.2f}"
            # Check width and truncate if necessary
            if c.stringWidth(basis_text) > 65:  # Column width limit
                basis_text = f"{transaction['cost_basis']:,.0f}"
            c.drawRightString(col_positions['cost_basis'], y_pos, basis_text)
            
            # Column (f) - Code: Leave blank for crypto transactions
            
            # Column (g) - Adjustment: Leave blank (no adjustments for crypto)
            
            # Column (h) - Gain/Loss: Right-aligned with proper formatting
            gain_loss = transaction['gain_loss']
            if gain_loss < 0:
                gain_loss_text = f"({abs(gain_loss):,.2f})"  # Parentheses for losses
            else:
                gain_loss_text = f"{gain_loss:,.2f}"
            
            # Check width and truncate if necessary
            if c.stringWidth(gain_loss_text) > 70:  # Column width limit
                if gain_loss < 0:
                    gain_loss_text = f"({abs(gain_loss):,.0f})"
                else:
                    gain_loss_text = f"{gain_loss:,.0f}"
            
            c.drawRightString(col_positions['gain_loss'], y_pos, gain_loss_text)
        
        # Add totals on final page - positioned in official totals row
        if page_num == total_pages and len(transactions) > 0:
            # Position totals in the official "Totals" row at bottom of table
            totals_y = table_start_y - (14 * row_height) - 15
            
            # Calculate totals for ALL transactions
            total_proceeds = sum(t['proceeds'] for t in all_transactions)
            total_basis = sum(t['cost_basis'] for t in all_transactions)
            total_gain_loss = sum(t['gain_loss'] for t in all_transactions)
            
            # Use slightly larger bold font for totals
            c.setFont("Helvetica-Bold", 6)
            
            # Draw totals with same column alignment
            total_proceeds_text = f"{total_proceeds:,.2f}"
            total_basis_text = f"{total_basis:,.2f}"
            
            c.drawRightString(col_positions['proceeds'], totals_y, total_proceeds_text)
            c.drawRightString(col_positions['cost_basis'], totals_y, total_basis_text)
            
            # Format total gain/loss
            if total_gain_loss < 0:
                total_gl_text = f"({abs(total_gain_loss):,.2f})"
            else:
                total_gl_text = f"{total_gain_loss:,.2f}"
            c.drawRightString(col_positions['gain_loss'], totals_y, total_gl_text)
        
        c.save()
        
        # Merge overlay with official template
        overlay_buffer.seek(0)
        overlay_reader = PyPDF2.PdfReader(overlay_buffer)
        overlay_page = overlay_reader.pages[0]
        
        # Combine template and data overlay
        template_page.merge_page(overlay_page)
        
        # Write final PDF to buffer
        pdf_writer = PyPDF2.PdfWriter()
        pdf_writer.add_page(template_page)
        pdf_writer.write(buffer)
        
        return True
        
    except Exception as e:
        st.error(f"Error creating form with official template: {e}")
        return False

def get_official_form_8949(tax_year):
    """Download official IRS Form 8949 for the specified tax year"""
    irs_urls = {
        2024: "https://www.irs.gov/pub/irs-pdf/f8949.pdf",
        2023: "https://www.irs.gov/pub/irs-prior/f8949--2023.pdf",
        2022: "https://www.irs.gov/pub/irs-prior/f8949--2022.pdf",
        2021: "https://www.irs.gov/pub/irs-prior/f8949--2021.pdf",
        2020: "https://www.irs.gov/pub/irs-prior/f8949--2020.pdf"
    }
    
    url = irs_urls.get(tax_year, irs_urls[2024])
    
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            return response.content
    except Exception as e:
        st.warning(f"Could not download official form: {e}")
    
    return None

def create_custom_form_8949(buffer, transactions, part_type, taxpayer_name, taxpayer_ssn, tax_year, box_type, page_num, total_pages, all_transactions):
    """Create custom Form 8949 if official template fails"""
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Form header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, f"Form 8949 ({tax_year})")
    c.setFont("Helvetica", 12)
    c.drawString(200, height - 50, "Sales and Other Dispositions of Capital Assets")
    
    # Taxpayer information
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 80, f"Name: {taxpayer_name}")
    c.drawString(400, height - 80, f"SSN: {taxpayer_ssn}")
    
    # Part header
    c.setFont("Helvetica-Bold", 12)
    if part_type == "Part I":
        c.drawString(50, height - 110, "Part I - Short-Term Capital Gains and Losses")
    else:
        c.drawString(50, height - 110, "Part II - Long-Term Capital Gains and Losses")
    
    # Box type
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 130, f"☑ {box_type}")
    
    # Table headers
    y_pos = height - 180
    c.setFont("Helvetica-Bold", 8)
    headers = [
        ("Description", 50),
        ("Date Acquired", 180),
        ("Date Sold", 240),
        ("Proceeds", 300),
        ("Cost Basis", 370),
        ("Code", 430),
        ("Adjustment", 470),
        ("Gain/Loss", 530)
    ]
    
    for header, x_pos in headers:
        c.drawString(x_pos, y_pos, header)
    
    # Draw table lines
    c.line(40, y_pos - 5, width - 40, y_pos - 5)
    
    # Transaction data
    c.setFont("Helvetica", 7)
    for i, transaction in enumerate(transactions[:14]):
        y_pos = height - 200 - (i * 15)
        
        data = [
            (transaction['description'][:25], 50),
            (transaction['date_acquired'].strftime('%m/%d/%Y'), 180),
            (transaction['date_sold'].strftime('%m/%d/%Y'), 240),
            (f"{transaction['proceeds']:,.2f}", 300),
            (f"{transaction['cost_basis']:,.2f}", 370),
            ("", 430),
            ("", 470),
            (f"{transaction['gain_loss']:,.2f}" if transaction['gain_loss'] >= 0 
             else f"({abs(transaction['gain_loss']):,.2f})", 530)
        ]
        
        for text, x_pos in data:
            c.drawString(x_pos, y_pos, str(text))
    
    # Totals (on last page only)
    if page_num == total_pages:
        totals_y = height - 200 - (14 * 15) - 20
        c.setFont("Helvetica-Bold", 8)
        c.drawString(50, totals_y, "TOTALS")
        
        total_proceeds = sum(t['proceeds'] for t in all_transactions)
        total_basis = sum(t['cost_basis'] for t in all_transactions)
        total_gain_loss = sum(t['gain_loss'] for t in all_transactions)
        
        c.drawString(300, totals_y, f"{total_proceeds:,.2f}")
        c.drawString(370, totals_y, f"{total_basis:,.2f}")
        c.drawString(530, totals_y, f"{total_gain_loss:,.2f}" if total_gain_loss >= 0 
                    else f"({abs(total_gain_loss):,.2f})")
    
    # Page footer
    c.setFont("Helvetica", 8)
    if total_pages > 1:
        c.drawString(50, 30, f"Page {page_num} of {total_pages}")
    c.drawRightString(width - 50, 30, f"Generated: {datetime.now().strftime('%m/%d/%Y')}")
    
    c.save()

def create_zip_file(pdf_files):
    """Create ZIP file containing all PDFs"""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for pdf_file in pdf_files:
            zip_file.writestr(pdf_file['filename'], pdf_file['content'])
    return zip_buffer.getvalue()

if __name__ == "__main__":
    main()
