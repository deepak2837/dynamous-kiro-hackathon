#!/usr/bin/env python3
"""
Create a simple test PDF for testing
"""
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def create_test_pdf():
    """Create a simple test PDF with medical content"""
    filename = "test_sample.pdf"
    
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    # Add some medical content
    c.drawString(100, height - 100, "Medical Study Material")
    c.drawString(100, height - 130, "")
    c.drawString(100, height - 160, "Chapter 1: Anatomy")
    c.drawString(100, height - 190, "The human heart has four chambers:")
    c.drawString(120, height - 220, "1. Right atrium")
    c.drawString(120, height - 250, "2. Right ventricle") 
    c.drawString(120, height - 280, "3. Left atrium")
    c.drawString(120, height - 310, "4. Left ventricle")
    c.drawString(100, height - 340, "")
    c.drawString(100, height - 370, "The cardiac cycle consists of systole and diastole.")
    c.drawString(100, height - 400, "Blood flows from the right ventricle to the lungs via")
    c.drawString(100, height - 430, "the pulmonary artery for oxygenation.")
    
    c.save()
    print(f"✅ Created test PDF: {filename}")

if __name__ == "__main__":
    create_test_pdf()
