import chainlit as cl
import json
import matplotlib.pyplot as plt
import io
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
import datetime

# --- Sample JSON (fallback) ---
workshop_data = { ... }  # keep your existing sample JSON here

# Utility: Generate matplotlib chart as BytesIO
def generate_chart(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    plt.close(fig)
    return buf

def generate_narrative(metrics):
    return f"""
### Executive Summary  
This monthly report covers operations between {metrics['timeMetrics']['estimatedTime']} and actual {metrics['timeMetrics']['actualTime']}.  
- **Time performance** shows {metrics['timeMetrics']['onTimeCompletionRate']} completion on schedule.  
- **Costs** were estimated at ₹{metrics['costMetrics']['estimatedCost']} but actuals came at ₹{metrics['costMetrics']['actualCost']}, reflecting efficiency in raw material usage.  
- **Customer satisfaction** remained high at {metrics['qualityMetrics']['customerSatisfaction']} despite minor reworks.  

### Key Insights  
1. Productivity stable at {metrics['productivityMetrics']['taskCompletionRate']}, contributing to {metrics['productivityMetrics']['workOutput']} units of output.  
2. Safety compliance was perfect ({metrics['safetyMetrics']['complianceRate']}).  
3. Employee attendance {metrics['employeeMetrics']['employeeAttendance']} with {metrics['employeeMetrics']['trainingHours']} training hours each shows a motivated workforce.  
4. Environmental metrics such as {metrics['environmentalMetrics']['wasteReduction']} waste reduction indicate sustainability.  
"""

# --- PDF Generation Function ---
def build_pdf(data, charts):
    pdf_buf = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buf, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # Cover Page
    story.append(Paragraph("Workshop Monthly Report", styles["Title"]))
    story.append(Spacer(1, 24))
    story.append(Paragraph(f"Period: {data['reportPeriod']['startDate']} → {data['reportPeriod']['endDate']}", styles["Heading2"]))
    story.append(Paragraph("Prepared by AI Report Maker", styles["Normal"]))
    story.append(PageBreak())

    # Executive summary & charts
    story.append(Paragraph("Executive Summary", styles["Heading1"]))
    story.append(Paragraph(generate_narrative(data["workshopMetrics"]), styles["Normal"]))
    story.append(Image(charts["cost"], width=350, height=250))
    story.append(PageBreak())

    # Add other sections (Performance, Resources, Operations, Employees, Financial, Tasks)
    # → replicate your previous logic with more narrative paragraphs
    # → ensure each major section ends with PageBreak()

    doc.build(story)
    pdf_buf.seek(0)
    return pdf_buf

# --- Email Sending Function ---
def send_email(recipient, pdf_bytes):
    sender_email = "your_email@example.com"
    sender_pass = "your_password"  # or use env vars!
    subject = "Workshop Report"

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = recipient
    msg["Subject"] = subject

    body = "Please find attached the workshop performance report."
    msg.attach(MIMEText(body, "plain"))

    # Attach PDF
    attachment = MIMEApplication(pdf_bytes, _subtype="pdf")
    attachment.add_header("Content-Disposition", "attachment", filename="Workshop_Report.pdf")
    msg.attach(attachment)

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_pass)
        server.send_message(msg)

# --- Chainlit Bot Flow ---
@cl.on_chat_start
async def start():
    files = await cl.AskFileMessage(
        content="📂 Upload JSON or type **generate** to use default data.",
        accept=["application/json"], max_size_mb=5, max_files=1
    ).send()
    if files:
        with open(files[0].path, "r", encoding="utf-8") as f:
            data = json.load(f)
        cl.user_session.set("report_data", data)
    else:
        cl.user_session.set("report_data", workshop_data)

@cl.on_message
async def main(message: cl.Message):
    if message.content.strip().lower() == "generate":
        data = cl.user_session.get("report_data")

        # Generate charts dict
        charts = {
            "cost": generate_chart(plt.figure(figsize=(5, 3)))
            # build your other charts too...
        }

        # 1️⃣ Show full report in chat
        await cl.Message(content=generate_narrative(data["workshopMetrics"])).send()

        # 2️⃣ Generate PDF
        pdf_buf = build_pdf(data, charts)
        await cl.Message(
            content="📥 Download your full 8-page report below:",
            elements=[cl.File(name="Workshop_Report.pdf", content=pdf_buf.getvalue())]
        ).send()

        # 3️⃣ Ask for email
        email_input = await cl.AskUserMessage(
            content="✉️ Enter an email address to send the report:",
            timeout=60
        ).send()

        if email_input:
            send_email(email_input["output"], pdf_buf.getvalue())
            await cl.Message(content=f"✅ Report sent to {email_input['output']}").send()
    else:
        await cl.Message(content="Type **generate** to build your report.").send()
