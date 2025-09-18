import chainlit as cl
import json
import matplotlib.pyplot as plt
import io
import datetime
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

# === SAMPLE JSON (fallback if user doesn’t upload) ===
workshop_data = {
    "reportPeriod": {"startDate": "2024-07-01", "endDate": "2024-07-31"},
    "workshopMetrics": {
        "timeMetrics": {
            "estimatedTime": "4 hours", "actualTime": "4 hours 10 minutes",
            "onTimeCompletionRate": "90%", "averageTaskDuration": "4.2 hours"
        },
        "costMetrics": {
            "estimatedCost": 650, "actualCost": 500,
            "costOverrunRate": "15%", "costEfficiency": "125 units/USD"
        },
        "qualityMetrics": {
            "reworkRate": "5%", "defectRate": "2%", "customerSatisfaction": "4.5/5"
        },
        "productivityMetrics": {
            "taskCompletionRate": "20 tasks/month", "workOutput": "100 units",
            "employeeProductivity": "5 tasks/employee"
        },
        "resourceUtilizationMetrics": {"equipmentUtilization": "80%", "laborUtilization": "75%"},
        "safetyMetrics": {"incidentRate": "1 incident/month", "complianceRate": "100%"},
        "financialMetrics": {"profitability": "₹50000", "returnOnInvestment": "20%"},
        "operationalMetrics": {
            "downtime": "5 hours/month", "inventoryTurnover": "3 times/month",
            "downtimeImpact": "High", "publicDisruptionDuration": "10 days"
        },
        "employeeMetrics": {
            "employeeAttendance": "95%", "trainingHours": "10 hours/employee",
            "employeeSatisfaction": "4/5", "workersAtStart": 10, "workersAtEnd": 9
        },
        "environmentalMetrics": {"wasteReduction": "80%", "energyConsumption": "2000 kWh"},
        "repurchasingMetrics": {"resourceRepurchasingRate": "20%"}
    },
    "workshopSchedule": [
        {
            "taskId": "T001", "taskName": "Vehicle Servicing",
            "startDate": "2024-07-01", "endDate": "2024-07-01",
            "estimatedCost": 650, "actualCost": 500,
            "expenseCategories": {
                "workers": {"estimatedCost": 400, "actualCost": 350},
                "rawMaterial": {"estimatedCost": 250, "actualCost": 150}
            },
            "steps": [
                {"stepId": "S001", "stepName": "Tire Replacement", "employeeName": "John Doe",
                 "scheduledStartTime": "09:00", "scheduledEndTime": "10:00",
                 "actualStartTime": "09:05", "actualEndTime": "10:10", "status": "Completed"},
                {"stepId": "S002", "stepName": "Brake Inspection", "employeeName": "Jane Smith",
                 "scheduledStartTime": "10:00", "scheduledEndTime": "11:00",
                 "actualStartTime": "10:00", "actualEndTime": "11:00", "status": "Completed"}
            ]
        },
        {
            "taskId": "T002", "taskName": "Street Lamp Installation",
            "startDate": "2024-07-02", "endDate": "2024-07-02",
            "estimatedCost": 1100, "actualCost": 800,
            "expenseCategories": {
                "workers": {"estimatedCost": 500, "actualCost": 400},
                "rawMaterial": {"estimatedCost": 600, "actualCost": 400}
            },
            "steps": [
                {"stepId": "S003", "stepName": "Fill with Gravel", "employeeName": "Alice Brown",
                 "scheduledStartTime": "09:00", "scheduledEndTime": "10:00",
                 "actualStartTime": "09:00", "actualEndTime": "10:00", "status": "Completed"}
            ]
        }
    ]
}

# === Helper: save matplotlib chart to BytesIO ===
def chart_to_buf(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    plt.close(fig)
    return buf

# === Generate multiple charts ===
def generate_charts(metrics, data):
    charts = {}

    # Cost Comparison
    fig, ax = plt.subplots()
    ax.bar(["Estimated", "Actual"],
           [metrics["costMetrics"]["estimatedCost"], metrics["costMetrics"]["actualCost"]],
           color=["#3498db", "#2ecc71"])
    ax.set_title("Cost Comparison")
    ax.set_ylabel("₹")
    charts["cost"] = chart_to_buf(fig)

    # Expense Breakdown (from first task)
    exp = data["workshopSchedule"][0]["expenseCategories"]
    fig, ax = plt.subplots()
    ax.pie([exp["workers"]["actualCost"], exp["rawMaterial"]["actualCost"]],
           labels=["Workers", "Raw Material"], autopct="%1.1f%%",
           colors=["#f39c12", "#8e44ad"])
    ax.set_title("Expense Breakdown")
    charts["expenses"] = chart_to_buf(fig)

    # Resource Utilization
    fig, ax = plt.subplots()
    ax.bar(["Equipment", "Labor"],
           [int(metrics["resourceUtilizationMetrics"]["equipmentUtilization"].strip("%")),
            int(metrics["resourceUtilizationMetrics"]["laborUtilization"].strip("%"))],
           color=["#e74c3c", "#16a085"])
    ax.set_title("Resource Utilization")
    ax.set_ylabel("%")
    charts["resources"] = chart_to_buf(fig)

    # Productivity vs Downtime
    fig, ax = plt.subplots()
    ax.bar(["Tasks Completed", "Downtime (hrs)"], [20, 5], color=["#2980b9", "#c0392b"])
    ax.set_title("Productivity vs Downtime")
    charts["downtime"] = chart_to_buf(fig)

    # Employee Satisfaction
    fig, ax = plt.subplots()
    ax.bar(["Satisfaction"], [float(metrics["employeeMetrics"]["employeeSatisfaction"].split("/")[0])],
           color="#9b59b6")
    ax.set_ylim(0, 5)
    ax.set_title("Employee Satisfaction (out of 5)")
    charts["satisfaction"] = chart_to_buf(fig)

    # Energy Consumption
    fig, ax = plt.subplots()
    ax.bar(["Energy Consumption"], [2000], color="#27ae60")
    ax.set_title("Energy Consumption (kWh)")
    charts["energy"] = chart_to_buf(fig)

    return charts

# === Build PDF with 7–8 pages ===
def build_pdf(data, metrics, charts):
    pdf_buf = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buf, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # Page 1 – Cover
    story.append(Paragraph("Workshop Performance Report", styles["Title"]))
    story.append(Spacer(1, 24))
    story.append(Paragraph(f"Period: {data['reportPeriod']['startDate']} → {data['reportPeriod']['endDate']}", styles["Heading2"]))
    story.append(Paragraph(f"Generated on {datetime.date.today()}", styles["Normal"]))
    story.append(PageBreak())

    # Page 2 – Executive Summary
    story.append(Paragraph("Executive Summary", styles["Heading1"]))
    story.append(Paragraph(
        f"This report provides a comprehensive overview of workshop activities. "
        f"Despite estimated costs of ₹{metrics['costMetrics']['estimatedCost']}, "
        f"actual spending was only ₹{metrics['costMetrics']['actualCost']}, "
        f"showing effective cost control. Time metrics reveal "
        f"{metrics['timeMetrics']['onTimeCompletionRate']} tasks were completed on schedule. "
        f"Customer satisfaction remains high at {metrics['qualityMetrics']['customerSatisfaction']}."
    , styles["Normal"]))
    story.append(Image(charts["cost"], width=350, height=250))
    story.append(PageBreak())

    # Page 3 – Cost & Quality
    story.append(Paragraph("Cost & Quality Metrics", styles["Heading1"]))
    story.append(Paragraph(
        f"Rework rate was {metrics['qualityMetrics']['reworkRate']} and defect rate was "
        f"{metrics['qualityMetrics']['defectRate']}, which are both below industry average. "
        f"Cost efficiency stands at {metrics['costMetrics']['costEfficiency']}, highlighting strong performance."
    , styles["Normal"]))
    story.append(Image(charts["expenses"], width=300, height=300))
    story.append(PageBreak())

    # Page 4 – Productivity & Resources
    story.append(Paragraph("Productivity & Resource Utilization", styles["Heading1"]))
    story.append(Paragraph(
        f"Task completion rate reached {metrics['productivityMetrics']['taskCompletionRate']}, "
        f"with total output of {metrics['productivityMetrics']['workOutput']}. "
        f"Employee productivity averaged {metrics['productivityMetrics']['employeeProductivity']}. "
        f"Equipment utilization was {metrics['resourceUtilizationMetrics']['equipmentUtilization']}, "
        f"and labor utilization {metrics['resourceUtilizationMetrics']['laborUtilization']}."
    , styles["Normal"]))
    story.append(Image(charts["resources"], width=350, height=250))
    story.append(Image(charts["downtime"], width=350, height=250))
    story.append(PageBreak())

    # Page 5 – Employee Insights
    story.append(Paragraph("Employee Insights", styles["Heading1"]))
    story.append(Paragraph(
        f"Attendance reached {metrics['employeeMetrics']['employeeAttendance']}, "
        f"and training hours averaged {metrics['employeeMetrics']['trainingHours']} per employee. "
        f"Satisfaction score is {metrics['employeeMetrics']['employeeSatisfaction']}, "
        f"indicating a healthy workforce."
    , styles["Normal"]))
    story.append(Image(charts["satisfaction"], width=300, height=250))
    story.append(PageBreak())

    # Page 6 – Operational Metrics
    story.append(Paragraph("Operational Performance", styles["Heading1"]))
    story.append(Paragraph(
        f"Downtime totaled {metrics['operationalMetrics']['downtime']} "
        f"with {metrics['operationalMetrics']['inventoryTurnover']} inventory turnover. "
        f"Disruption lasted {metrics['operationalMetrics']['publicDisruptionDuration']}."
    , styles["Normal"]))
    story.append(PageBreak())

    # Page 7 – Environmental & Financial
    story.append(Paragraph("Environmental & Financial Metrics", styles["Heading1"]))
    story.append(Paragraph(
        f"Waste reduction reached {metrics['environmentalMetrics']['wasteReduction']}, "
        f"with energy consumption of {metrics['environmentalMetrics']['energyConsumption']}. "
        f"Financial performance was strong, with profitability of {metrics['financialMetrics']['profitability']} "
        f"and ROI of {metrics['financialMetrics']['returnOnInvestment']}."
    , styles["Normal"]))
    story.append(Image(charts["energy"], width=300, height=250))
    story.append(PageBreak())

    # Page 8 – Task Breakdown
    story.append(Paragraph("Detailed Task Breakdown", styles["Heading1"]))
    table_data = [["Task ID", "Task Name", "Est. Cost", "Act. Cost", "Status"]]
    for task in data["workshopSchedule"]:
        table_data.append([task["taskId"], task["taskName"],
                           f"₹{task['estimatedCost']}", f"₹{task['actualCost']}", "Completed"])
    table = Table(table_data)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(table)
    for task in data["workshopSchedule"]:
        story.append(Paragraph(f"{task['taskName']} Steps:", styles["Heading2"]))
        for step in task["steps"]:
            story.append(Paragraph(f"- {step['stepName']} by {step['employeeName']} [{step['status']}]", styles["Normal"]))

    doc.build(story)
    pdf_buf.seek(0)
    return pdf_buf

# === Chainlit Bot Flow ===
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
        metrics = data["workshopMetrics"]
        charts = generate_charts(metrics, data)

        # Build summary string for preview
        summary = f"""
### 📝 Workshop Report ({data['reportPeriod']['startDate']} → {data['reportPeriod']['endDate']})

- ⏱ Time: Estimated {metrics['timeMetrics']['estimatedTime']}, Actual {metrics['timeMetrics']['actualTime']}
- 💰 Cost: Estimated ₹{metrics['costMetrics']['estimatedCost']}, Actual ₹{metrics['costMetrics']['actualCost']}
- 📦 Output: {metrics['productivityMetrics']['workOutput']} units
- 😀 Customer Satisfaction: {metrics['qualityMetrics']['customerSatisfaction']}
- 👷 Employees: Start {metrics['employeeMetrics']['workersAtStart']} → End {metrics['employeeMetrics']['workersAtEnd']}
        """
        await cl.Message(content="✅ Report generated! Here is a summary preview:").send()
        await cl.Message(content=summary).send()

        # Build PDF
        pdf_buf = build_pdf(data, metrics, charts)

        # Send PDF
        await cl.Message(
            content="📥 Download your detailed report:",
            elements=[cl.File(name="Workshop_Report.pdf", content=pdf_buf.getvalue())]
        ).send()
    else:
        await cl.Message(content="Type **generate** to build the report.").send()
