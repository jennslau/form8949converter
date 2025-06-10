import streamlit as st
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import io
import zipfile
from datetime import datetime

def main():
    st.set_page_config(
        page_title="CSV to PDF Form Filler",
        page_icon="📄",
        layout="wide"
    )
    
    st.title("📄 CSV to PDF Form Filler")
    st.markdown("Upload a CSV file and generate filled PDF forms for each row of data.")
    
    # Sidebar for configuration
    st.sidebar.header("Configuration")
    
    # Template selection
    template_type = st.sidebar.selectbox(
        "Choose PDF Template Type:",
        ["Simple Form", "Invoice Template", "Certificate Template", "Report Template"]
    )
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("Step 1: Upload CSV File")
        uploaded_file = st.file_uploader(
            "Choose a CSV file",
            type="csv",
            help="Upload a CSV file with the data you want to use in your PDFs"
        )
        
        if uploaded_file is not None:
            try:
                # Read the CSV file
                df = pd.read_csv(uploaded_file)
                st.success(f"✅ CSV loaded successfully! Found {len(df)} rows and {len(df.columns)} columns.")
                
                # Display preview
                st.subheader("Data Preview")
                st.dataframe(df.head())
                
                # Show column names
                st.subheader("Available Columns")
                st.write("These are the column names you can use in your PDF:")
                for i, col in enumerate(df.columns, 1):
                    st.write(f"{i}. **{col}**")
                
            except Exception as e:
                st.error(f"Error reading CSV file: {str(e)}")
                df = None
        else:
            df = None
    
    with col2:
        st.header("Step 2: Configure PDF Template")
        
        if df is not None:
            # Column mapping section
            st.subheader("Map CSV Columns to PDF Fields")
            
            # Get template fields based on selection
            template_fields = get_template_fields(template_type)
            
            # Create mapping interface
            field_mapping = {}
            for field_name, field_description in template_fields.items():
                selected_column = st.selectbox(
                    f"{field_description}:",
                    [""] + list(df.columns),
                    key=f"mapping_{field_name}"
                )
                if selected_column:
                    field_mapping[field_name] = selected_column
            
            # PDF generation settings
            st.subheader("PDF Settings")
            page_size = st.selectbox("Page Size:", ["Letter", "A4"])
            font_size = st.slider("Font Size:", 8, 16, 12)
            
            # Generate PDFs button
            if st.button("🚀 Generate PDFs", type="primary"):
                if field_mapping:
                    try:
                        # Generate PDFs
                        pdf_files = generate_pdfs(df, field_mapping, template_type, page_size, font_size)
                        
                        if len(pdf_files) == 1:
                            # Single PDF download
                            st.download_button(
                                label="📥 Download PDF",
                                data=pdf_files[0]['content'],
                                file_name=pdf_files[0]['filename'],
                                mime="application/pdf"
                            )
                        else:
                            # Multiple PDFs - create zip
                            zip_data = create_zip_file(pdf_files)
                            st.download_button(
                                label="📦 Download All PDFs (ZIP)",
                                data=zip_data,
                                file_name=f"generated_pdfs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                                mime="application/zip"
                            )
                        
                        st.success(f"✅ Generated {len(pdf_files)} PDF file(s) successfully!")
                        
                    except Exception as e:
                        st.error(f"Error generating PDFs: {str(e)}")
                else:
                    st.warning("Please map at least one CSV column to a PDF field.")
        
        else:
            st.info("👆 Please upload a CSV file first to configure the PDF template.")

def get_template_fields(template_type):
    """Define fields for different template types"""
    templates = {
        "Simple Form": {
            "name": "Name/Title",
            "email": "Email Address",
            "phone": "Phone Number",
            "address": "Address",
            "notes": "Additional Notes"
        },
        "Invoice Template": {
            "invoice_number": "Invoice Number",
            "client_name": "Client Name",
            "client_address": "Client Address",
            "date": "Invoice Date",
            "amount": "Total Amount",
            "description": "Service Description"
        },
        "Certificate Template": {
            "recipient_name": "Recipient Name",
            "course_name": "Course/Achievement",
            "date_completed": "Completion Date",
            "instructor": "Instructor/Issuer",
            "grade": "Grade/Score"
        },
        "Report Template": {
            "title": "Report Title",
            "author": "Author Name",
            "date": "Report Date",
            "summary": "Executive Summary",
            "data_point_1": "Key Metric 1",
            "data_point_2": "Key Metric 2"
        }
    }
    return templates.get(template_type, templates["Simple Form"])

def generate_pdfs(df, field_mapping, template_type, page_size, font_size):
    """Generate PDF files based on the CSV data and template"""
    pdf_files = []
    
    # Set page size
    if page_size == "A4":
        page_format = A4
    else:
        page_format = letter
    
    for index, row in df.iterrows():
        # Create PDF content
        buffer = io.BytesIO()
        
        if template_type == "Simple Form":
            create_simple_form_pdf(buffer, row, field_mapping, page_format, font_size)
        elif template_type == "Invoice Template":
            create_invoice_pdf(buffer, row, field_mapping, page_format, font_size)
        elif template_type == "Certificate Template":
            create_certificate_pdf(buffer, row, field_mapping, page_format, font_size)
        else:  # Report Template
            create_report_pdf(buffer, row, field_mapping, page_format, font_size)
        
        # Generate filename
        name_field = field_mapping.get('name') or field_mapping.get('recipient_name') or field_mapping.get('client_name') or field_mapping.get('title')
        if name_field and name_field in row:
            filename = f"{str(row[name_field]).replace(' ', '_')}_{index+1}.pdf"
        else:
            filename = f"document_{index+1}.pdf"
        
        pdf_files.append({
            'filename': filename,
            'content': buffer.getvalue()
        })
    
    return pdf_files

def create_simple_form_pdf(buffer, row, field_mapping, page_format, font_size):
    """Create a simple form PDF"""
    c = canvas.Canvas(buffer, pagesize=page_format)
    width, height = page_format
    
    # Title
    c.setFont("Helvetica-Bold", font_size + 4)
    c.drawString(50, height - 50, "Information Form")
    
    # Form fields
    y_position = height - 100
    c.setFont("Helvetica", font_size)
    
    for field_name, column_name in field_mapping.items():
        if column_name in row:
            field_label = get_template_fields("Simple Form")[field_name]
            value = str(row[column_name]) if pd.notna(row[column_name]) else ""
            
            c.setFont("Helvetica-Bold", font_size)
            c.drawString(50, y_position, f"{field_label}:")
            c.setFont("Helvetica", font_size)
            c.drawString(200, y_position, value)
            y_position -= 30
    
    c.save()

def create_invoice_pdf(buffer, row, field_mapping, page_format, font_size):
    """Create an invoice PDF"""
    c = canvas.Canvas(buffer, pagesize=page_format)
    width, height = page_format
    
    # Header
    c.setFont("Helvetica-Bold", font_size + 6)
    c.drawString(50, height - 50, "INVOICE")
    
    # Invoice details
    y_position = height - 100
    c.setFont("Helvetica", font_size)
    
    # Right side - Invoice number and date
    if 'invoice_number' in field_mapping and field_mapping['invoice_number'] in row:
        invoice_num = str(row[field_mapping['invoice_number']])
        c.drawString(width - 200, y_position, f"Invoice #: {invoice_num}")
    
    if 'date' in field_mapping and field_mapping['date'] in row:
        date_val = str(row[field_mapping['date']])
        c.drawString(width - 200, y_position - 20, f"Date: {date_val}")
    
    # Client information
    y_position -= 60
    c.setFont("Helvetica-Bold", font_size)
    c.drawString(50, y_position, "Bill To:")
    c.setFont("Helvetica", font_size)
    
    if 'client_name' in field_mapping and field_mapping['client_name'] in row:
        client_name = str(row[field_mapping['client_name']])
        c.drawString(50, y_position - 20, client_name)
    
    if 'client_address' in field_mapping and field_mapping['client_address'] in row:
        client_address = str(row[field_mapping['client_address']])
        c.drawString(50, y_position - 40, client_address)
    
    # Service details
    y_position -= 100
    if 'description' in field_mapping and field_mapping['description'] in row:
        description = str(row[field_mapping['description']])
        c.drawString(50, y_position, f"Description: {description}")
    
    if 'amount' in field_mapping and field_mapping['amount'] in row:
        amount = str(row[field_mapping['amount']])
        c.setFont("Helvetica-Bold", font_size + 2)
        c.drawString(50, y_position - 40, f"Total Amount: ${amount}")
    
    c.save()

def create_certificate_pdf(buffer, row, field_mapping, page_format, font_size):
    """Create a certificate PDF"""
    c = canvas.Canvas(buffer, pagesize=page_format)
    width, height = page_format
    
    # Border
    c.rect(30, 30, width-60, height-60, stroke=1, fill=0)
    c.rect(40, 40, width-80, height-80, stroke=1, fill=0)
    
    # Title
    c.setFont("Helvetica-Bold", font_size + 8)
    title_text = "CERTIFICATE OF COMPLETION"
    title_width = c.stringWidth(title_text, "Helvetica-Bold", font_size + 8)
    c.drawString((width - title_width) / 2, height - 100, title_text)
    
    # Content
    y_position = height - 200
    c.setFont("Helvetica", font_size + 2)
    
    # Recipient name
    if 'recipient_name' in field_mapping and field_mapping['recipient_name'] in row:
        recipient = str(row[field_mapping['recipient_name']])
        c.setFont("Helvetica-Bold", font_size + 4)
        recipient_width = c.stringWidth(recipient, "Helvetica-Bold", font_size + 4)
        c.drawString((width - recipient_width) / 2, y_position, recipient)
        y_position -= 60
    
    # Course name
    if 'course_name' in field_mapping and field_mapping['course_name'] in row:
        course = str(row[field_mapping['course_name']])
        c.setFont("Helvetica", font_size + 2)
        course_text = f"has successfully completed: {course}"
        course_width = c.stringWidth(course_text, "Helvetica", font_size + 2)
        c.drawString((width - course_width) / 2, y_position, course_text)
        y_position -= 60
    
    # Date and instructor
    if 'date_completed' in field_mapping and field_mapping['date_completed'] in row:
        date_val = str(row[field_mapping['date_completed']])
        c.drawString(100, y_position, f"Date: {date_val}")
    
    if 'instructor' in field_mapping and field_mapping['instructor'] in row:
        instructor = str(row[field_mapping['instructor']])
        c.drawString(width - 250, y_position, f"Instructor: {instructor}")
    
    c.save()

def create_report_pdf(buffer, row, field_mapping, page_format, font_size):
    """Create a report PDF"""
    c = canvas.Canvas(buffer, pagesize=page_format)
    width, height = page_format
    
    # Header
    if 'title' in field_mapping and field_mapping['title'] in row:
        title = str(row[field_mapping['title']])
        c.setFont("Helvetica-Bold", font_size + 4)
        c.drawString(50, height - 50, title)
    
    # Author and date
    y_position = height - 80
    c.setFont("Helvetica", font_size)
    
    if 'author' in field_mapping and field_mapping['author'] in row:
        author = str(row[field_mapping['author']])
        c.drawString(50, y_position, f"Author: {author}")
    
    if 'date' in field_mapping and field_mapping['date'] in row:
        date_val = str(row[field_mapping['date']])
        c.drawString(width - 200, y_position, f"Date: {date_val}")
    
    y_position -= 60
    
    # Summary section
    if 'summary' in field_mapping and field_mapping['summary'] in row:
        summary = str(row[field_mapping['summary']])
        c.setFont("Helvetica-Bold", font_size)
        c.drawString(50, y_position, "Executive Summary:")
        c.setFont("Helvetica", font_size)
        
        # Word wrap for summary
        words = summary.split()
        lines = []
        current_line = []
        for word in words:
            test_line = ' '.join(current_line + [word])
            if c.stringWidth(test_line, "Helvetica", font_size) < width - 100:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
        
        for line in lines:
            y_position -= 20
            c.drawString(50, y_position, line)
    
    # Data points
    y_position -= 60
    for field_name in ['data_point_1', 'data_point_2']:
        if field_name in field_mapping and field_mapping[field_name] in row:
            field_label = get_template_fields("Report Template")[field_name]
            value = str(row[field_mapping[field_name]])
            c.setFont("Helvetica-Bold", font_size)
            c.drawString(50, y_position, f"{field_label}:")
            c.setFont("Helvetica", font_size)
            c.drawString(200, y_position, value)
            y_position -= 30
    
    c.save()

def create_zip_file(pdf_files):
    """Create a ZIP file containing all PDFs"""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for pdf_file in pdf_files:
            zip_file.writestr(pdf_file['filename'], pdf_file['content'])
    return zip_buffer.getvalue()

if __name__ == "__main__":
    main()