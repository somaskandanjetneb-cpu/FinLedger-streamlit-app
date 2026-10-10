from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate,Table,TableStyle,Paragraph,Spacer
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.enums import TA_CENTER,TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from config import FONTS_DIR
FONT="Helvetica"
p=FONTS_DIR/"NotoSans-Regular.ttf"
if p.exists(): pdfmetrics.registerFont(TTFont("NotoSans",str(p))); FONT="NotoSans"
def rs(x,symbol="₹"):
    return f"{symbol} {float(x):,.2f}" if FONT=="NotoSans" or symbol!="₹" else f"Rs. {float(x):,.2f}"
def report_pdf(rows,company,start,end):
    out=BytesIO(); doc=SimpleDocTemplate(out,pagesize=A4,leftMargin=28,rightMargin=28,topMargin=30,bottomMargin=30)
    styles=getSampleStyleSheet(); title=ParagraphStyle("T",parent=styles["Title"],fontName=FONT,alignment=TA_CENTER)
    right=ParagraphStyle("R",parent=styles["Normal"],fontName=FONT,alignment=TA_RIGHT)
    story=[Paragraph(company["company_name"],title),Paragraph(company["address"] or "",ParagraphStyle("A",parent=styles["Normal"],fontName=FONT,alignment=TA_CENTER)),Spacer(1,8),Paragraph(f"Income & Expense Report — {start} to {end}",title),Spacer(1,10)]
    data=[["Date","Type","Category","Amount","Details"]]+[[r["trans_date"],r["trans_type"],r["category"],rs(r["amount"],company["currency_symbol"]),r["details"] or ""] for r in rows]
    t=Table(data,repeatRows=1,colWidths=[65,60,90,80,180])
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#1e3a8a")),("TEXTCOLOR",(0,0),(-1,0),colors.white),("FONTNAME",(0,0),(-1,-1),FONT),("FONTSIZE",(0,0),(-1,-1),8),("GRID",(0,0),(-1,-1),.3,colors.grey),("ALIGN",(3,1),(3,-1),"RIGHT")]))
    story.append(t); inc=sum(r["amount"] for r in rows if r["trans_type"]=="Income"); exp=sum(r["amount"] for r in rows if r["trans_type"]=="Expense")
    story += [Spacer(1,10),Paragraph(f"<b>Total Income:</b> {rs(inc,company['currency_symbol'])}",right),Paragraph(f"<b>Total Expense:</b> {rs(exp,company['currency_symbol'])}",right),Paragraph(f"<b>Net:</b> {rs(inc-exp,company['currency_symbol'])}",right)]
    def footer(canvas,doc): canvas.saveState(); canvas.setFont(FONT,8); canvas.drawCentredString(A4[0]/2,16,f"Page {doc.page}"); canvas.restoreState()
    doc.build(story,onFirstPage=footer,onLaterPages=footer); out.seek(0); return out.getvalue()
