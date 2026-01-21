#!/usr/bin/env python3
"""
Create a simple test PDF file for OCR testing
"""

import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def create_test_pdf():
    """Create a simple PDF with text for OCR testing"""
    
    filename = "/tmp/test_medical_document.pdf"
    
    # Create a simple PDF with medical content
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    # Add some medical text content
    c.setFont("Helvetica", 12)
    
    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 100, "Medical Study Notes")
    
    # Content
    c.setFont("Helvetica", 12)
    y_position = height - 150
    
    medical_content = [
        "Cardiovascular System:",
        "- The heart has four chambers: two atria and two ventricles",
        "- Blood flows from right atrium → right ventricle → lungs",
        "- Oxygenated blood returns to left atrium → left ventricle → body",
        "",
        "Respiratory System:",
        "- Alveoli are the site of gas exchange",
        "- Oxygen diffuses from alveoli into blood",
        "- Carbon dioxide diffuses from blood into alveoli",
        "",
        "Key Medical Terms:",
        "- Tachycardia: Fast heart rate (>100 bpm)",
        "- Bradycardia: Slow heart rate (<60 bpm)",
        "- Hypertension: High blood pressure",
        "- Hypotension: Low blood pressure"
    ]
    
    for line in medical_content:
        c.drawString(100, y_position, line)
        y_position -= 20
    
    c.save()
    
    print(f"✅ Created test PDF: {filename}")
    print(f"📄 File size: {os.path.getsize(filename)} bytes")
    
    return filename

if __name__ == "__main__":
    create_test_pdf()
