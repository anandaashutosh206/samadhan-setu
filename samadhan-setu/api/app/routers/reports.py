import io

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.routers.analytics import by_district, by_domain, outcomes, overview

router = APIRouter(prefix="/reports", tags=["reports"])


def _base_doc(buffer: io.BytesIO) -> SimpleDocTemplate:
    return SimpleDocTemplate(buffer, pagesize=A4, topMargin=2 * cm, bottomMargin=2 * cm)


@router.get("/challenge/{challenge_id}.pdf")
def challenge_report(challenge_id: str, db: Session = Depends(get_db)):
    challenge = db.get(models.Challenge, challenge_id)
    if challenge is None:
        raise HTTPException(status_code=404, detail={"detail": "Challenge not found", "code": "NOT_FOUND"})

    styles = getSampleStyleSheet()
    buffer = io.BytesIO()
    doc = _base_doc(buffer)
    story = [
        Paragraph("Samadhan Setu — Challenge Report", styles["Title"]),
        Spacer(1, 12),
        Paragraph(challenge.title, styles["Heading2"]),
        Spacer(1, 8),
        Paragraph(challenge.description, styles["BodyText"]),
        Spacer(1, 12),
    ]

    rows = [
        ["Field", "Value"],
        ["Domain", challenge.domain],
        ["Severity", challenge.severity],
        ["Status", challenge.status],
        ["District", challenge.district],
        ["Priority score", str(challenge.priority_score)],
        ["Beneficiaries (est.)", str(challenge.beneficiaries_estimate)],
        ["Upvotes", str(challenge.upvote_count)],
        ["Submitted at", challenge.created_at.strftime("%Y-%m-%d %H:%M UTC")],
    ]
    table = Table(rows, colWidths=[5 * cm, 10 * cm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4F46E5")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    story.append(table)

    if challenge.ai_summary:
        story.append(Spacer(1, 12))
        story.append(Paragraph("AI Summary", styles["Heading3"]))
        story.append(Paragraph(challenge.ai_summary, styles["BodyText"]))

    if challenge.ai_keywords:
        story.append(Spacer(1, 8))
        story.append(Paragraph("Keywords: " + ", ".join(challenge.ai_keywords), styles["BodyText"]))

    doc.build(story)
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=challenge_{challenge_id}.pdf"},
    )


@router.get("/analytics.pdf")
def analytics_report(db: Session = Depends(get_db)):
    ov = overview(db)
    domains = by_domain(db)
    districts = by_district(db)
    outc = outcomes(db)

    styles = getSampleStyleSheet()
    buffer = io.BytesIO()
    doc = _base_doc(buffer)
    story = [
        Paragraph("Samadhan Setu — Analytics Report", styles["Title"]),
        Spacer(1, 12),
        Paragraph(
            f"Total challenges: {ov.total_challenges} | Universities: {ov.total_universities} | "
            f"Industries: {ov.total_industries} | Proposals: {ov.total_proposals} | Projects: {ov.total_projects}",
            styles["BodyText"],
        ),
        Spacer(1, 12),
        Paragraph("Challenges by Domain", styles["Heading2"]),
    ]
    domain_rows = [["Domain", "Count"]] + [[d.domain, str(d.count)] for d in domains]
    story.append(_styled_table(domain_rows))

    story.append(Spacer(1, 12))
    story.append(Paragraph("Challenges by District", styles["Heading2"]))
    district_rows = [["District", "Count", "Avg Priority"]] + [[d.district, str(d.count), str(d.avg_priority)] for d in districts]
    story.append(_styled_table(district_rows))

    story.append(Spacer(1, 12))
    story.append(Paragraph("Outcomes", styles["Heading2"]))
    outcome_rows = [
        ["Metric", "Value"],
        ["Patents filed", str(outc.patents_filed)],
        ["Startups spawned", str(outc.startups_spawned)],
        ["Pilots deployed", str(outc.pilots_deployed)],
        ["Total beneficiaries impacted", str(outc.total_beneficiaries_impacted)],
    ]
    story.append(_styled_table(outcome_rows))

    doc.build(story)
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=analytics_report.pdf"},
    )


def _styled_table(rows: list[list[str]]) -> Table:
    table = Table(rows, colWidths=[8 * cm, 4 * cm, 4 * cm][: len(rows[0])])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0D9488")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
            ]
        )
    )
    return table
