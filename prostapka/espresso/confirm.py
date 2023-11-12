from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.rl_config import defaultPageSize
from reportlab.platypus import Paragraph
from reportlab.lib.fonts import addMapping
from reportlab.graphics.shapes import *
from .models import Order, Client, Jdg


def confirm(request, pk):
    order = Order.objects.get(pk=pk)
    buf = io.BytesIO()
    img_file = 'logo.jpg'

    pdfmetrics.registerFont(TTFont('NotoSans', 'NotoSans-Thin.ttf'))
    addMapping('NotoSans', 0, 0, 'NotoSans')

    c = canvas.Canvas(buf, pagesize=A4)
    c.setFont("Helvetica", 12) 

    # Pobierz dane klienta z powiązanego obiektu Order
    client = order.client
    jdg = Jdg.objects.first() 

    data = [
        [f'Potwierdzenie złożenia zamówienia z dnia {order.date1}', ''],
        [f'Zamawiający: {client.client} ', f'Dane urządzenia:'],
        [f'nr kontaktowy: {client.phone}', f'marka: {order.brand}'],
        [f'', f'numer seryjny: {order.serial}']
    ]
    t = Table(data, colWidths=[80*mm, 80*mm])
    t.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'NotoSans'),
        ('WORDWRAP', (0, 0), (-1, -1), 'True'),
        ('LINEBELOW', (0,-1), (-1,-1), 2, colors.black)
    ]))

    t.wrapOn(c, 160*mm, 10*mm)  
    t.drawOn(c, 35*mm, 260*mm) 

    d1 = f'Uwagi: {order.uwagi}'
    my_style = ParagraphStyle(name="My Style", fontName="NotoSans", fontSize=10, borderWidth=0, borderColor='black', shrink=1)
    d1 = Paragraph(d1, my_style)
    d1.wrapOn(c, 160*mm, 10*mm)  
    d1.drawOn(c, 35*mm, 245*mm) 

    d2 = f'Opis awarii: {order.todo}'
    my_style1 = ParagraphStyle(name="My Style1", fontName="NotoSans", fontSize=10, borderWidth=0, borderColor='black', shrink=1)
    d2 = Paragraph(d2, my_style1)
    d2.wrapOn(c, 160*mm, 10*mm)  
    d2.drawOn(c, 35*mm, 220*mm) 

    data1 = [
      ['Odbiór sprzętu - podpis klienta','Odbiór sprzętu - podpis serwisu']
    ]
    t1 = Table(data1, colWidths=[80*mm, 80*mm])
    t1.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'NotoSans'),
        ('LINEBELOW', (0,-1), (-1,-1), 2, colors.black)
      ]))
    t1.wrapOn(c, 160*mm, 10*mm)
    t1.drawOn(c, 35*mm, 200*mm)

    t.wrapOn(c, 160*mm, 10*mm)  
    t.drawOn(c, 35*mm, 110*mm) 
    d1.wrapOn(c, 160*mm, 10*mm)  
    d1.drawOn(c, 35*mm, 95*mm)
    d2.wrapOn(c, 160*mm, 10*mm)  
    d2.drawOn(c, 35*mm, 70*mm)  
    t1.wrapOn(c, 160*mm, 10*mm)
    t1.drawOn(c, 35*mm, 50*mm)

    c.drawImage(img_file, 15*mm, 250*mm, width=50,  preserveAspectRatio=True, mask='auto')
    c.drawImage(img_file, 15*mm, 100*mm, width=50,  preserveAspectRatio=True, mask='auto')   



    c.setFont("NotoSans", 6)
    c.drawCentredString(110*mm,20*mm, jdg.pole1)
    c.drawCentredString(110*mm,15*mm, jdg.pole2)
    c.drawCentredString(110*mm,10*mm, jdg.pole3)
    c.drawCentredString(110*mm,5*mm, jdg.pole4)

    c.showPage()
    c.save()
    buf.seek(0)
    return FileResponse(buf, as_attachment=True, filename=f'potwierdzenie_{order.id}.pdf')