# pdf_generator.py - PDF generation functions
import os
from datetime import datetime
from database import get_db

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("Warning: ReportLab not installed. PDF generation disabled.")

def generate_memory_pdf(pdf_type='summary'):
    """Generate PDF of memories."""
    if not PDF_AVAILABLE:
        raise Exception("ReportLab not installed. Install with: pip install reportlab")
    
    # Get data from database
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("SELECT name FROM user_profile LIMIT 1")
    profile = cursor.fetchone()
    user_name = profile[0] if profile else "Our Family"
    
    cursor.execute("SELECT text, category, memory_date, year FROM memories ORDER BY year DESC")
    memories = cursor.fetchall()
    
    # Create PDF (simplified)
    filename = f"family_memories_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = os.path.join('uploads', filename)
    
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    story.append(Paragraph(f"Family Memories of {user_name}", styles['Heading1']))
    story.append(Spacer(1, 12))
    
    for memory in memories[:20]:  # Limit to 20 memories
        text, category, memory_date, year = memory
        story.append(Paragraph(f"{year}: {text[:200]}...", styles['Normal']))
        story.append(Spacer(1, 6))
    
    doc.build(story)
    return filepath

def generate_family_album_pdf():
    """Generate family album PDF."""
    if not PDF_AVAILABLE:
        raise Exception("ReportLab not installed")
    
    # Similar to above but with images
    filename = f"family_album_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = os.path.join('uploads', filename)
    
    # Simplified version
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    story.append(Paragraph("Family Album", styles['Heading1']))
    story.append(Paragraph(f"Created on {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
    
    doc.build(story)
    return filepath