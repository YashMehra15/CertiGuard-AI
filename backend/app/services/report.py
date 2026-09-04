from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

def make_report(result):
    buf=BytesIO(); doc=SimpleDocTemplate(buf,pagesize=A4,rightMargin=36,leftMargin=36,topMargin=36,bottomMargin=36)
    styles=getSampleStyleSheet(); story=[Paragraph("CertiGuard AI — Certificate Authenticity Report",styles["Title"]),Spacer(1,12)]
    rows=[("Verdict",result.get("verdict")),("Authenticity confidence",f"{result.get('authenticity_confidence',0)}%"),("Tampering risk",f"{result.get('tampering_risk',0)}%"),("Issuer",result.get("issuer")),("Certificate ID",result.get("certificate_id") or "Not detected"),("SHA-256",result.get("sha256"))]
    f=result.get("fields",{})
    rows += [("Student",f.get("student_name") or "Not detected"),("Course",f.get("course_line") or "Not detected"),("Issue date",f.get("issue_date") or "Not detected")]
    t=Table(rows,colWidths=[150,360]);t.setStyle(TableStyle([("GRID",(0,0),(-1,-1),.5,colors.grey),("BACKGROUND",(0,0),(0,-1),colors.whitesmoke),("VALIGN",(0,0),(-1,-1),"TOP")]))
    story += [t,Spacer(1,16),Paragraph("Evidence",styles["Heading2"])]
    for e in result.get("evidence",[]):story.append(Paragraph(f"<b>{e['status']} — {e['name']}</b>: {e['detail']}",styles["BodyText"]))
    if result.get("concrete_tamper_signals"):
        story += [Spacer(1,10),Paragraph("Tampering signals",styles["Heading2"])]
        for x in result["concrete_tamper_signals"]:story.append(Paragraph("• "+x,styles["BodyText"]))
    story += [Spacer(1,14),Paragraph(result.get("disclaimer",""),styles["BodyText"])]
    doc.build(story);return buf.getvalue()
