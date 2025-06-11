def create_form_with_official_template(buffer, transactions, part_type, taxpayer_name, taxpayer_ssn, tax_year, box_type, page_num, total_pages, all_transactions):
    """Create Form 8949 using official IRS template with precise field mapping to light blue autofill boxes"""
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
        
        # CORRECTED COORDINATES - Measured precisely to align with light blue autofill boxes
        
        # Taxpayer information fields (blue header boxes at top)
        name_field_x = 65      # Left edge of name blue box
        name_field_y = height - 148
        ssn_field_x = 675      # Right edge of SSN blue box  
        ssn_field_y = height - 148
        
        # Checkbox positions (measured from actual form)
        if part_type == "Part I":
            checkbox_base_y = height - 429   # Part I checkboxes
            # CRITICAL: Start exactly where light blue rows begin
            table_start_y = height - 567     # First light blue row position
        else:
            checkbox_base_y = height - 350   # Part II checkboxes  
            table_start_y = height - 567     # First light blue row for Part II
        
        checkbox_x = 42
        
        # PRECISE column positions - mapped to center/align within each light blue box
        col_positions = {
            'description': 55,      # Column (a) - left edge of blue box + padding
            'date_acquired': 210,   # Column (b) - center of blue box
            'date_sold': 280,       # Column (c) - center of blue box
            'proceeds': 380,        # Column (d) - right edge of blue box
            'cost_basis': 460,      # Column (e) - right edge of blue box  
            'code': 510,            # Column (f) - center of small blue box
            'adjustment': 560,      # Column (g) - right edge of blue box
            'gain_loss': 630        # Column (h) - right edge of rightmost blue box
        }
        
        # CORRECTED row spacing - matches exact height of light blue boxes
        row_height = 17.5  # Measured from blue box to blue box
        
        # Fill taxpayer information in header blue boxes
        c.setFont("Helvetica", 9)
        c.drawString(name_field_x, name_field_y, taxpayer_name[:45])
        c.drawRightString(ssn_field_x, ssn_field_y, taxpayer_ssn)
        
        # Check appropriate box based on selection
        c.setFont("Helvetica", 10)
        box_letter = box_type.split()[1]  # Extract A, B, or C
        
        if part_type == "Part I":
            if box_letter == "A":
                c.drawString(checkbox_x, checkbox_base_y, "✓")
            elif box_letter == "B": 
                c.drawString(checkbox_x, checkbox_base_y - 18, "✓")
            elif box_letter == "C":
                c.drawString(checkbox_x, checkbox_base_y - 36, "✓")
        else:  # Part II - maps A->D, B->E, C->F
            if box_letter == "A":  # Maps to Box D for long-term
                c.drawString(checkbox_x, checkbox_base_y, "✓")
            elif box_letter == "B":  # Maps to Box E for long-term
                c.drawString(checkbox_x, checkbox_base_y - 18, "✓")
            elif box_letter == "C":  # Maps to Box F for long-term
                c.drawString(checkbox_x, checkbox_base_y - 36, "✓")
        
        # CORRECTED font size to fit cleanly in blue boxes
        c.setFont("Helvetica", 6.5)  # Smaller font to fit in blue cells
        
        # Fill transaction data in light blue autofill boxes
        for i, transaction in enumerate(transactions[:14]):  # Maximum 14 transactions per page
            y_pos = table_start_y - (i * row_height)
            
            # Format data to fit within blue box constraints
            description = transaction['description'][:28]  # Truncate to fit blue box width
            date_acquired = transaction['date_acquired'].strftime('%m/%d/%Y')
            date_sold = transaction['date_sold'].strftime('%m/%d/%Y')
            
            # Column (a) - Description: Left-aligned within blue box
            c.drawString(col_positions['description'], y_pos, description)
            
            # Column (b) - Date acquired: Centered within blue box
            date_acq_width = c.stringWidth(date_acquired)
            c.drawString(col_positions['date_acquired'] - date_acq_width/2, y_pos, date_acquired)
            
            # Column (c) - Date sold: Centered within blue box
            date_sold_width = c.stringWidth(date_sold)
            c.drawString(col_positions['date_sold'] - date_sold_width/2, y_pos, date_sold)
            
            # Column (d) - Proceeds: Right-aligned within blue box
            proceeds_text = f"{transaction['proceeds']:,.2f}"
            c.drawRightString(col_positions['proceeds'], y_pos, proceeds_text)
            
            # Column (e) - Cost basis: Right-aligned within blue box
            basis_text = f"{transaction['cost_basis']:,.2f}"
            c.drawRightString(col_positions['cost_basis'], y_pos, basis_text)
            
            # Column (f) - Code: Centered (leave blank for crypto - no codes needed)
            # c.drawString(col_positions['code'], y_pos, "")
            
            # Column (g) - Adjustment: Right-aligned (leave blank - no adjustments)
            # c.drawRightString(col_positions['adjustment'], y_pos, "")
            
            # Column (h) - Gain/Loss: Right-aligned within rightmost blue box
            gain_loss = transaction['gain_loss']
            if gain_loss < 0:
                gain_loss_text = f"({abs(gain_loss):,.2f})"  # Parentheses for losses (IRS standard)
            else:
                gain_loss_text = f"{gain_loss:,.2f}"
            c.drawRightString(col_positions['gain_loss'], y_pos, gain_loss_text)
        
        # Add totals on final page only (in totals row at bottom)
        if page_num == total_pages and len(transactions) > 0:
            # Position totals in the official totals row
            totals_y = table_start_y - (14 * row_height) - 8
            
            # Calculate totals for ALL transactions (not just this page)
            total_proceeds = sum(t['proceeds'] for t in all_transactions)
            total_basis = sum(t['cost_basis'] for t in all_transactions)
            total_gain_loss = sum(t['gain_loss'] for t in all_transactions)
            
            # Use bold font for totals
            c.setFont("Helvetica-Bold", 6.5)
            
            # Draw totals aligned with their respective columns
            total_proceeds_text = f"{total_proceeds:,.2f}"
            total_basis_text = f"{total_basis:,.2f}"
            
            c.drawRightString(col_positions['proceeds'], totals_y, total_proceeds_text)
            c.drawRightString(col_positions['cost_basis'], totals_y, total_basis_text)
            
            # Format total gain/loss with parentheses if negative
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
