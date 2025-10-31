from app.utils.dp_utils import fetch_products
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER
from tkinter import filedialog
from datetime import datetime
from tkinter import filedialog, messagebox
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def export_all_to_pdf():
    file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
    if not file_path:
        return
    rows = fetch_products()
    try:
        doc = SimpleDocTemplate(file_path, pagesize=landscape(A4))
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle('Title', parent=styles['Heading1'], alignment=TA_CENTER, fontSize=20, textColor=colors.HexColor('#2c3e50'))
        elements.append(Paragraph("📦 Complete Inventory Report", title_style))
        elements.append(Spacer(1, 12))
        
        # Date
        subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'], alignment=TA_CENTER, fontSize=11, textColor=colors.HexColor('#7f8c8d'))
        elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", subtitle_style))
        elements.append(Spacer(1, 18))

        # Summary totals
        total_required = sum(int(r["required_qty"] or 0) for r in rows)
        total_good = sum(int(r["good_qty"] or 0) for r in rows)
        total_damaged = sum(int(r["damaged_qty"] or 0) for r in rows)
        total_gift = sum(int(r["gift"] or 0) for r in rows)
        total_stock = sum(int(r["total_qty"] or 0) for r in rows)
        
        summary_table = Table([
            ["Summary", "Required", "Good", "Damaged", "Gift", "Total Stock"],
            ["Totals", f"{total_required:,}", f"{total_good:,}", f"{total_damaged:,}", f"{total_gift:,}", f"{total_stock:,}"]
        ], colWidths=[2*inch, 1.3*inch, 1.3*inch, 1.3*inch, 1.3*inch, 1.3*inch])
        
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 11),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('TOPPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#ecf0f1')),
            ('FONTNAME', (0,1), (-1,-1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,1), (-1,-1), 10),
            ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#bdc3c7'))
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 22))

        # Data table
        headers = ['ID','Name','Code','Description','Cost','Retail','Required','Good','Damaged','Gift','Total','Note']
        data = [headers]
        
        for r in rows:
            data.append([
                str(r["id"]), 
                str(r["name"])[:22], 
                str(r["code"]), 
                (str(r["description"])[:32] if r["description"] else ""),
                f"${float(r['cost'] or 0):.2f}", 
                f"${float(r['retail'] or 0):.2f}",
                str(int(r["required_qty"] or 0)), 
                str(int(r["good_qty"] or 0)), 
                str(int(r["damaged_qty"] or 0)),
                str(int(r["gift"] or 0)), 
                str(int(r["total_qty"] or 0)), 
                str(r["note"] or "")[:20]
            ])
            
        col_widths = [0.4*inch, 1.5*inch, 0.9*inch, 1.7*inch, 0.75*inch, 0.75*inch, 0.85*inch, 0.65*inch, 0.85*inch, 0.65*inch, 0.65*inch, 1.3*inch]
        table = Table(data, colWidths=col_widths, repeatRows=1)
        
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 9),
            ('BOTTOMPADDING', (0,0), (-1,0), 10),
            ('TOPPADDING', (0,0), (-1,0), 10),
            ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,1), (-1,-1), 8),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8f9fa')]),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#bdc3c7')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (0,0), (-1,-1), 4),
            ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 18))
        
        # Footer
        footer_style = ParagraphStyle('Footer', parent=styles['Normal'], alignment=TA_CENTER, fontSize=8, textColor=colors.HexColor('#7f8c8d'))
        footer = Paragraph(f"Total Products: {len(rows)} | © {datetime.now().year} Inventory Management System", footer_style)
        elements.append(footer)
        
        doc.build(elements)
        messagebox.showinfo("Success", f"✅ PDF exported to:\n{file_path}")
    except Exception as e:
        messagebox.showerror("Error", f"❌ An error occurred while creating PDF:\n{str(e)}")


def export_mismatch_to_pdf():
    file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
    if not file_path:
        return
    rows = fetch_products()
    mismatched = [r for r in rows if int(r["required_qty"] or 0) != int(r["total_qty"] or 0)]
    
    if not mismatched:
        messagebox.showinfo("No Mismatch", "ℹ️ No mismatched products found.")
        return
        
    try:
        doc = SimpleDocTemplate(file_path, pagesize=landscape(A4))
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle('Title', parent=styles['Heading1'], alignment=TA_CENTER, fontSize=20, textColor=colors.HexColor('#e74c3c'))
        elements.append(Paragraph("⚠️ Mismatched Inventory Report", title_style))
        elements.append(Spacer(1, 12))
        
        # Date & Warning
        subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'], alignment=TA_CENTER, fontSize=11, textColor=colors.HexColor('#7f8c8d'))
        elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", subtitle_style))
        elements.append(Spacer(1, 12))
        
        warning_style = ParagraphStyle('Warning', parent=styles['Normal'], alignment=TA_CENTER, fontSize=11, textColor=colors.HexColor('#e74c3c'), fontName='Helvetica-Bold')
        warning = Paragraph(f"⚠️ {len(mismatched)} products have quantity mismatches (Required ≠ Total)", warning_style)
        elements.append(warning)
        elements.append(Spacer(1, 18))

        # Data table
        data = [["ID","Name","Code","Description","Required","Good","Damaged","Gift","Total","Variance"]]
        
        for r in mismatched:
            req = int(r["required_qty"] or 0)
            tot = int(r["total_qty"] or 0)
            variance = tot - req
            data.append([
                str(r["id"]), 
                str(r["name"])[:22], 
                str(r["code"]), 
                (str(r["description"])[:35] if r["description"] else ""),
                str(req), 
                str(int(r["good_qty"] or 0)), 
                str(int(r["damaged_qty"] or 0)), 
                str(int(r["gift"] or 0)), 
                str(tot), 
                f"{variance:+d}"
            ])
            
        col_widths = [0.4*inch, 1.6*inch, 0.9*inch, 2*inch, 0.9*inch, 0.75*inch, 0.9*inch, 0.7*inch, 0.75*inch, 0.85*inch]
        table = Table(data, colWidths=col_widths, repeatRows=1)
        
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e74c3c')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 9),
            ('BOTTOMPADDING', (0,0), (-1,0), 10),
            ('TOPPADDING', (0,0), (-1,0), 10),
            ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,1), (-1,-1), 8),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8f9fa')]),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#bdc3c7')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (0,0), (-1,-1), 4),
            ('RIGHTPADDING', (0,0), (-1,-1), 4),
            # Highlight variance column
            ('BACKGROUND', (9,1), (9,-1), colors.HexColor('#fff3cd')),
            ('TEXTCOLOR', (9,1), (9,-1), colors.HexColor('#856404')),
            ('FONTNAME', (9,1), (9,-1), 'Helvetica-Bold'),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 18))
        
        # Footer
        footer_style = ParagraphStyle('Footer', parent=styles['Normal'], alignment=TA_CENTER, fontSize=8, textColor=colors.HexColor('#7f8c8d'))
        footer = Paragraph(f"Mismatched Products: {len(mismatched)} | © {datetime.now().year} Inventory Management System", footer_style)
        elements.append(footer)
        
        doc.build(elements)
        messagebox.showinfo("Exported", f"✅ Exported PDF to:\n{file_path}")
    except Exception as e:
        messagebox.showerror("Error", f"❌ An error occurred while creating PDF:\n{str(e)}")
