from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
import os
from datetime import datetime
from database import get_db

def generate_memory_pdf(pdf_type="all"):
    """Generate PDF for specific memory types (backward compatibility)."""
    try:
        # This is for backward compatibility with app.py
        # Map old pdf_type values to appropriate functions
        
        if pdf_type == "album" or pdf_type == "all":
            return generate_family_album_pdf()
        else:
            # For other types (timeline, etc.), generate a simple PDF
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"{pdf_type}_memories_{timestamp}.pdf"
            
            db = get_db()
            cursor = db.cursor()
            
            # Get memories for this type
            if pdf_type == "timeline":
                cursor.execute("""
                    SELECT text, year, memory_date 
                    FROM memories 
                    WHERE year IS NOT NULL 
                    ORDER BY year
                """)
                title = "Memory Timeline"
            else:
                cursor.execute("SELECT text, category FROM memories")
                title = f"{pdf_type.capitalize()} Memories"
            
            memories = cursor.fetchall()
            
            # Create PDF
            doc = SimpleDocTemplate(output_path, pagesize=letter)
            story = []
            styles = getSampleStyleSheet()
            
            story.append(Paragraph(title, styles['Heading1']))
            story.append(Spacer(1, 0.25*inch))
            
            for memory in memories:
                if len(memory) >= 2:
                    story.append(Paragraph(f"<b>{memory[1] if memory[1] else 'Undated'}</b>", styles['Heading2']))
                    story.append(Paragraph(memory[0], styles['Normal']))
                    story.append(Spacer(1, 0.25*inch))
            
            doc.build(story)
            return output_path
            
    except Exception as e:
        print(f"Memory PDF error: {e}")
        return generate_simple_pdf()

def generate_family_album_pdf():
    """Generate family album PDF with actual content."""
    try:
        # Create output filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"family_album_{timestamp}.pdf"
        
        # Get data from database
        db = get_db()
        cursor = db.cursor()
        
        # Get memories
        cursor.execute("""
            SELECT id, text, category, memory_date, year, created_at 
            FROM memories 
            ORDER BY year DESC, created_at DESC
        """)
        memories = cursor.fetchall()
        
        # Get media
        cursor.execute("""
            SELECT id, filename, original_filename, file_type, title, description, 
                   memory_date, year, created_at 
            FROM media 
            WHERE file_type = 'image'
            ORDER BY created_at DESC
        """)
        media_items = cursor.fetchall()
        
        # Create PDF document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#2c3e50'),
            alignment=1  # Center
        )
        
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=20,
            textColor=colors.HexColor('#34495e'),
            alignment=1
        )
        
        memory_style = ParagraphStyle(
            'MemoryText',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=12,
            textColor=colors.HexColor('#2c3e50'),
            leading=14
        )
        
        # Title Page
        story.append(Spacer(1, 2*inch))
        story.append(Paragraph("Family Memory Album", title_style))
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph(f"Created on {datetime.now().strftime('%B %d, %Y')}", subtitle_style))
        story.append(PageBreak())
        
        # Memories Section
        if memories:
            story.append(Paragraph("Family Memories", styles['Heading1']))
            story.append(Spacer(1, 0.25*inch))
            
            for memory in memories:
                memory_id, text, category, memory_date, year, created_at = memory
                
                # Memory header with date
                date_str = memory_date if memory_date else f"Year: {year}" if year else "Undated"
                story.append(Paragraph(f"<b>{date_str}</b> - {category if category else 'Memory'}", styles['Heading2']))
                
                # Memory text
                story.append(Paragraph(text, memory_style))
                
                # Try to add associated image if available
                cursor.execute("""
                    SELECT m.filename, m.title 
                    FROM media m 
                    WHERE m.memory_date = ? OR m.year = ?
                    LIMIT 1
                """, (memory_date, year))
                associated_media = cursor.fetchone()
                
                if associated_media:
                    img_path = os.path.join('uploads', associated_media[0])
                    if os.path.exists(img_path):
                        try:
                            img = Image(img_path, width=4*inch, height=3*inch)
                            img.hAlign = 'CENTER'
                            story.append(img)
                            story.append(Paragraph(f"<i>{associated_media[1]}</i>", styles['Italic']))
                        except:
                            pass  # Skip if image can't be loaded
                
                story.append(Spacer(1, 0.5*inch))
            
            story.append(PageBreak())
        
        # Media Gallery Section
        if media_items:
            story.append(Paragraph("Photo Gallery", styles['Heading1']))
            story.append(Spacer(1, 0.25*inch))
            
            # Create table for image grid (2 columns)
            image_data = []
            row = []
            
            for media in media_items:
                media_id, filename, original, file_type, title, desc, mdate, year, created = media
                img_path = os.path.join('uploads', filename)
                
                if os.path.exists(img_path):
                    try:
                        # Create image with caption
                        img = Image(img_path, width=2.5*inch, height=2*inch)
                        caption = Paragraph(f"<b>{title if title else original}</b><br/>{desc if desc else ''}", 
                                           ParagraphStyle('Caption', parent=styles['Normal'], fontSize=9))
                        
                        if len(row) < 2:
                            row.append([img, caption])
                        else:
                            image_data.append(row)
                            row = [[img, caption]]
                    except:
                        pass  # Skip problematic images
            
            if row:
                image_data.append(row)
            
            if image_data:
                # Create table
                table = Table(image_data, colWidths=[3*inch, 3*inch])
                table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 10),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
                ]))
                story.append(table)
        
        # Generate PDF
        doc.build(story)
        print(f"✅ PDF generated: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"❌ PDF generation error: {e}")
        # Fallback to simple PDF if detailed fails
        return generate_simple_pdf()

def generate_simple_pdf():
    """Fallback simple PDF generator."""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"family_album_simple_{timestamp}.pdf"
        
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        story.append(Paragraph("Family Memory Album", styles['Heading1']))
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph("Your memories and photos are safe and preserved.", styles['Normal']))
        
        doc.build(story)
        return output_path
    except Exception as e:
        print(f"❌ Even simple PDF failed: {e}")
        return None