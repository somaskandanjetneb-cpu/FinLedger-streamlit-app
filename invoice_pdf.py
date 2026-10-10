from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.enums import TA_RIGHT,TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from config import FONTS_DIR
FONT="Helvetica"; p=FONTS_DIR/"NotoSans-Regular.ttf"
if p.exists(): pdfmetrics.registerFont(TTFont("NotoSans",str(p))); FONT="NotoSans"
def invoice_pdf(r,c):
    out=BytesIO(); doc=SimpleDocTemplate(out,pagesize=A4,leftMargin=40,rightMargin=40,topMargin=40,bottomMargin=40)
    st=getSampleStyleSheet(); title=ParagraphStyle("t",parent=st["Title"],fontName=FONT,alignment=TA_CENTER,fontSize=20); right=ParagraphStyle("r",parent=st["Normal"],fontName=FONT,alignment=TA_RIGHT)
    sym=c["currency_symbol"] or "₹"
    def m(x): return f"{sym} {float(x):,.2f}" if FONT=="NotoSans" or sym!="₹" else f"Rs. {float(x):,.2f}"
    story=[Paragraph(c["company_name"],title),Paragraph(c["address"] or "",ParagraphStyle("a",parent=st["Normal"],fontName=FONT,alignment=TA_CENTER)),Paragraph(f"{c['phone'] or ''}  {c['email'] or ''}",ParagraphStyle("b",parent=st["Normal"],fontName=FONT,alignment=TA_CENTER)),Spacer(1,18),Paragraph(f"<b>INVOICE</b>  {r['invoice_no']}",title),Spacer(1,12)]
    story.append(Table([[Paragraph("<b>Bill To</b>",st["Normal"]),Paragraph(f"<b>Date:</b> {r['invoice_date']}<br/><b>GSTIN:</b> {c['gstin'] or ''}",st["Normal"])],[f"{r['customer_name']}<br/>{r['customer_address'] or ''}<br/>{r['customer_phone'] or ''}<br/>{r['customer_email'] or ''}",""]],colWidths=[280,220]))
    story.append(Spacer(1,18))
    data=[["Description","Amount"],[r["description"] or "Service / Product",m(r["amount"])],["Tax",m(r["tax"])],["Total",m(r["total"])]]
    t=Table(data,colWidths=[350,150]); t.setStyle(TableStyle([("FONTNAME",(0,0),(-1,-1),FONT),("GRID",(0,0),(-1,-1),.5,colors.grey),("BACKGROUND",(0,0),(-1,0),colors.HexColor("#1e3a8a")),("TEXTCOLOR",(0,0),(-1,0),colors.white),("ALIGN",(1,1),(1,-1),"RIGHT"),("BACKGROUND",(0,-1),(-1,-1),colors.HexColor("#e0e7ff"))]))
    story += [t,Spacer(1,15),Paragraph(f"<b>Notes:</b> {r['notes'] or ''}",st["Normal"]),Spacer(1,30),Paragraph("Thank you for your business.",ParagraphStyle("c",parent=st["Normal"],fontName=FONT,alignment=TA_CENTER))]
    doc.build(story); out.seek(0); return out.getvalue()
