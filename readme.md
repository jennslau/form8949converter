# CSV to PDF Form Filler

A simple web application that converts CSV data into filled PDF forms. Upload a CSV file, map the columns to PDF fields, and generate professional PDFs for each row of data.

## Features

- 📊 Upload CSV files with your data
- 📄 Choose from 4 different PDF templates:
  - Simple Form
  - Invoice Template
  - Certificate Template
  - Report Template
- 🎨 Customize font size and page format
- 📦 Download individual PDFs or bulk download as ZIP
- 🌐 Easy-to-use web interface

## Step-by-Step Setup Guide

### Step 1: Create a GitHub Account (if you don't have one)

1. Go to [GitHub.com](https://github.com)
2. Click "Sign up" in the top right corner
3. Follow the instructions to create your account

### Step 2: Create a New Repository

1. Once logged into GitHub, click the green "New" button (or the "+" icon in the top right)
2. Name your repository (e.g., "csv-pdf-converter")
3. Make sure it's set to "Public"
4. Check the box "Add a README file"
5. Click "Create repository"

### Step 3: Upload Your Files to GitHub

1. In your new repository, click "uploading an existing file"
2. Upload these 3 files one by one:
   - `app.py` (the main application file)
   - `requirements.txt` (the dependencies file)
   - `README.md` (this instruction file)

**Important:** Make sure the main file is named exactly `app.py` - Streamlit looks for this specific name.

### Step 4: Deploy to Streamlit

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "Sign in" and use your GitHub account
3. Click "New app"
4. Select your repository from the dropdown
5. Make sure the main file path is set to `app.py`
6. Click "Deploy!"

### Step 5: Wait for Deployment

- Streamlit will automatically install the required packages
- This usually takes 2-3 minutes
- You'll see a "Your app is live!" message when it's ready

## How to Use the Application

### 1. Prepare Your CSV File

Your CSV should have column headers that describe your data. For example:

```csv
Name,Email,Phone,Address,Amount
John Doe,john@email.com,555-0123,123 Main St,$500
Jane Smith,jane@email.com,555-0456,456 Oak Ave,$750
```

### 2. Upload and Configure

1. **Upload CSV**: Click "Choose a CSV file" and select your file
2. **Choose Template**: Select the PDF template that best fits your needs
3. **Map Fields**: Match your CSV columns to the PDF fields
4. **Adjust Settings**: Set your preferred font size and page format

### 3. Generate PDFs

1. Click "Generate PDFs"
2. For single rows: Download the PDF directly
3. For multiple rows: Download a ZIP file containing all PDFs

## PDF Template Types

### Simple Form
Perfect for basic information forms, contact sheets, or general data collection.
- Fields: Name, Email, Phone, Address, Notes

### Invoice Template
Professional invoices for billing clients.
- Fields: Invoice Number, Client Name, Client Address, Date, Amount, Description

### Certificate Template
Elegant certificates for courses, achievements, or recognition.
- Fields: Recipient Name, Course/Achievement, Completion Date, Instructor, Grade

### Report Template
Professional reports with summaries and key metrics.
- Fields: Title, Author, Date, Executive Summary, Key Metrics

## Troubleshooting

**App won't start?**
- Check that your main file is named `app.py`
- Verify all files are uploaded to GitHub
- Make sure your repository is public

**CSV upload issues?**
- Ensure your CSV has proper headers
- Check for special characters in column names
- Save your file as CSV format (not Excel)

**PDF generation problems?**
- Make sure you've mapped at least one field
- Check that your CSV data doesn't have empty required fields

## Customization Options

You can modify the application by editing `app.py`:

- **Add new templates**: Create new template functions in the `generate_pdfs()` section
- **Change styling**: Modify the PDF creation functions to adjust fonts, colors, and layouts
- **Add fields**: Extend the template field mappings in `get_template_fields()`

## Support

If you encounter any issues:

1. Check that all files are properly uploaded to GitHub
2. Verify your CSV file format is correct
3. Make sure you've mapped the required fields
4. Try refreshing the Streamlit app

## File Structure

```
your-repository/
├── app.py              # Main application file
├── requirements.txt    # Python dependencies
└── README.md          # This instruction file
```

## Next Steps

Once your app is running:

1. Share the Streamlit URL with others who need to use the tool
2. Bookmark the URL for easy access
3. Consider adding more PDF templates by modifying the code
4. Explore Streamlit's documentation to add more features

Your app will be available at a URL like: `https://your-username-csv-pdf-converter-app-streamlit-app.py`

Enjoy your new CSV to PDF converter! 🎉