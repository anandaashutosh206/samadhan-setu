"""
Idempotent seed script for Samadhan Setu.
Usage:
  python scripts/seed.py            # seed if empty
  python scripts/seed.py --reset    # wipe and reseed
"""
import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "api"))

from app.database import Base, SessionLocal, engine  # noqa: E402
from app import models  # noqa: E402
from app.security import hash_password  # noqa: E402

random.seed(7)

DISTRICTS = [
    ("Ranchi", 23.3441, 85.3096), ("Dhanbad", 23.7957, 86.4304), ("East Singhbhum", 22.8046, 86.2029),
    ("West Singhbhum", 22.5680, 85.3339), ("Bokaro", 23.6693, 86.1511), ("Deoghar", 24.4823, 86.6957),
    ("Hazaribagh", 23.9925, 85.3617), ("Giridih", 24.1913, 86.3000), ("Palamu", 24.0432, 84.0730),
    ("Garhwa", 24.1526, 83.8079), ("Gumla", 23.0432, 84.5407), ("Simdega", 22.6162, 84.5111),
    ("Khunti", 23.0716, 85.2788), ("Lohardaga", 23.4333, 84.6833), ("Ramgarh", 23.6303, 85.5121),
    ("Chatra", 24.2072, 84.8697), ("Koderma", 24.4675, 85.5941), ("Godda", 24.8258, 87.2135),
    ("Sahibganj", 25.2425, 87.6438), ("Pakur", 24.6339, 87.8433), ("Dumka", 24.2685, 87.2497),
    ("Jamtara", 23.9631, 86.8054), ("Latehar", 23.7449, 84.5010), ("Seraikela Kharsawan", 22.6997, 85.9418),
]

UNIVERSITIES = [
    ("BIT Sindri", "BITS", "Dhanbad", "Government Engineering College", ["civil engineering", "mechanical engineering", "environmental engineering"], ["water resource management", "rural infrastructure"], True, "A"),
    ("NIT Jamshedpur", "NITJSR", "East Singhbhum", "National Institute of Technology", ["electrical engineering", "computer science", "civil engineering"], ["renewable energy", "smart infrastructure"], True, "A++"),
    ("IIT (ISM) Dhanbad", "IITISM", "Dhanbad", "Institute of National Importance", ["mining engineering", "environmental engineering", "geology"], ["mine safety", "groundwater systems"], True, "A++"),
    ("Ranchi University", "RU", "Ranchi", "State University", ["social sciences", "education", "public policy"], ["rural development", "tribal welfare"], False, "A"),
    ("BIT Mesra", "BITM", "Ranchi", "Deemed University", ["computer science", "biotechnology", "management"], ["health informatics", "agri-tech"], True, "A++"),
    ("XISS", "XISS", "Ranchi", "Autonomous Institute", ["management", "rural development", "social work"], ["livelihoods", "CSR management"], False, "A"),
    ("Central University of Jharkhand", "CUJ", "Ranchi", "Central University", ["environmental science", "life sciences", "law"], ["forest ecology", "public health"], True, "A"),
    ("NIFFT Ranchi", "NIFFT", "Ranchi", "National Institute", ["mechanical engineering", "design"], ["foundry technology", "assistive devices"], True, "A"),
    ("Jharkhand Rai University", "JRU", "Ranchi", "Private University", ["computer science", "design", "management"], ["accessibility tech", "digital education"], False, "B++"),
    ("Sarala Birla University", "SBU", "Ranchi", "Private University", ["agriculture", "biotechnology"], ["food technology", "crop science"], False, "B+"),
    ("Marwari College", "MC", "Ranchi", "Constituent College", ["education", "humanities"], ["adult literacy"], False, "B"),
    ("Vinoba Bhave University", "VBU", "Hazaribagh", "State University", ["agriculture", "rural development", "public administration"], ["MGNREGA outcomes", "panchayati raj"], False, "B++"),
]

INDUSTRIES = [
    ("Tata Steel Foundation", "Steel & CSR", "CSR", ["community development", "skilling"], "5-20 Cr", "East Singhbhum"),
    ("JharkhandAgri Startup", "AgriTech", "STARTUP", ["IoT sensors", "precision farming"], None, "Ranchi"),
    ("Usha Martin Ltd", "Manufacturing", "INDUSTRY", ["wire rope engineering", "prototyping"], None, "Ranchi"),
    ("CMPDI Innovation Hub", "Mining Tech", "INNOVATION_HUB", ["mine safety tech", "environmental monitoring"], None, "Ranchi"),
    ("Jharkhand Startup Hub", "Multi-sector", "INNOVATION_HUB", ["incubation", "seed funding"], None, "Ranchi"),
    ("HealthBridge MSME", "HealthTech", "MSME", ["telemedicine kits", "diagnostics"], None, "Dhanbad"),
    ("Adhaar Renewables", "Solar Energy", "STARTUP", ["solar micro-grids", "battery storage"], None, "Bokaro"),
    ("Coal India CSR Cell", "Mining CSR", "CSR", ["water infrastructure", "education"], "20+ Cr", "Dhanbad"),
    ("SwachhTech MSME", "WasteTech", "MSME", ["waste segregation systems"], None, "Ranchi"),
    ("Deshpande Foundation Jharkhand", "Social Innovation", "CSR", ["livelihoods", "entrepreneurship"], "1-5 Cr", "Ranchi"),
]

DOMAINS = list(models.DOMAINS)
SEVERITIES = ["low", "medium", "high", "critical"]
STATUSES_POOL = [
    "SUBMITTED", "AI_TRIAGED", "UNDER_REVIEW", "VALIDATED", "ROUTED",
    "ASSIGNED", "IN_PROGRESS", "PILOT", "IMPLEMENTED", "CLOSED",
]

CHALLENGE_TITLES = {
    "education": "School infrastructure gap in {d}",
    "agriculture": "Crop yield decline reported by farmers in {d}",
    "healthcare": "Primary healthcare access gap in {d}",
    "water_resources": "Drinking water scarcity in {d} villages",
    "environment": "Environmental degradation concern in {d}",
    "energy": "Power supply disruption in {d}",
    "urban_development": "Urban infrastructure strain in {d} town",
    "accessibility": "Accessibility gap for disabled citizens in {d}",
    "public_administration": "Service delivery delay reported in {d}",
    "rural_livelihoods": "Livelihood distress among rural households in {d}",
}

DEMO_USERS = [
    ("Citizen Demo", "citizen@jharkhand.gov.in", "CITIZEN", "Ranchi", None),
    ("Community Org Demo", "community@jharkhand.gov.in", "COMMUNITY_ORG", "Gumla", "Gumla PRI Federation"),
    ("University Admin Demo", "university@jharkhand.gov.in", "UNIVERSITY_ADMIN", "Dhanbad", "BIT Sindri"),
    ("Faculty Mentor Demo", "faculty@jharkhand.gov.in", "FACULTY_MENTOR", "Dhanbad", "BIT Sindri"),
    ("Student Demo", "student@jharkhand.gov.in", "STUDENT", "Dhanbad", "BIT Sindri"),
    ("Industry Partner Demo", "industry@jharkhand.gov.in", "INDUSTRY_PARTNER", "Ranchi", "JharkhandAgri Startup"),
    ("Govt Official Demo", "govt@jharkhand.gov.in", "GOVT_OFFICIAL", "Ranchi", "Dept. of Higher & Technical Education"),
    ("Super Admin Demo", "admin@jharkhand.gov.in", "SUPER_ADMIN", "Ranchi", None),
]
DEMO_PASSWORD = "Demo@1234"


def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def seed():
    db = SessionLocal()
    if db.query(models.User).count() > 0:
        print("Database already seeded. Use --reset to wipe and reseed.")
        db.close()
        return

    print("Seeding demo users...")
    users = {}
    for name, email, role, district, org in DEMO_USERS:
        u = models.User(name=name, email=email, password_hash=hash_password(DEMO_PASSWORD), role=role, district=district, org_name=org)
        db.add(u)
        users[role] = u
    db.flush()

    print("Seeding universities...")
    universities = []
    for name, code, district, type_, disc, research, incub, naac in UNIVERSITIES:
        lat, lng = next(((la, lo) for d, la, lo in DISTRICTS if d == district), (23.3, 85.3))
        u = models.University(
            name=name, code=code, district=district, type=type_, disciplines=disc, research_areas=research,
            has_incubation=incub, naac_grade=naac, contact_email=f"{code.lower()}@jharkhand.edu.in",
            lat=lat + random.uniform(-0.05, 0.05), lng=lng + random.uniform(-0.05, 0.05),
            capacity_score=random.uniform(50, 95), active_project_count=random.randint(0, 4),
        )
        db.add(u)
        universities.append(u)
    db.flush()

    print("Seeding industries...")
    industries = []
    for name, sector, type_, caps, csr_range, district in INDUSTRIES:
        ind = models.Industry(name=name, sector=sector, type=type_, capabilities=caps, csr_budget_range=csr_range, district=district, contact_email=f"contact@{name.split()[0].lower()}.com")
        db.add(ind)
        industries.append(ind)
    db.flush()

    print("Seeding 60 challenges (with 3 deliberate near-duplicate pairs)...")
    challenges = []
    now = datetime.now(timezone.utc)
    for i in range(60):
        district, lat, lng = random.choice(DISTRICTS)
        domain = random.choice(DOMAINS)
        severity = random.choice(SEVERITIES)
        status = random.choice(STATUSES_POOL)
        title = CHALLENGE_TITLES[domain].format(d=district) + f" #{i+1}"
        description = (
            f"Community members in {district} district have raised concerns regarding {domain.replace('_', ' ')} "
            f"issues affecting daily life, with severity assessed as {severity}. Local stakeholders have requested "
            f"government and institutional intervention to address the root causes and provide sustainable solutions."
        )
        c = models.Challenge(
            title=title, description=description, domain=domain, severity=severity, status=status,
            district=district, lat=lat + random.uniform(-0.1, 0.1), lng=lng + random.uniform(-0.1, 0.1),
            submitted_by_id=users["CITIZEN"].id, ai_confidence=round(random.uniform(0.55, 0.95), 2),
            ai_keywords=[domain.replace("_", " "), district.lower(), severity],
            ai_summary=description[:140] + "...",
            upvote_count=random.randint(0, 60),
            priority_score=round(random.uniform(20, 95), 2),
            beneficiaries_estimate=random.randint(50, 4000),
            created_at=now - timedelta(days=random.randint(1, 175)),
        )
        db.add(c)
        challenges.append(c)
    db.flush()

    # 3 deliberate near-duplicate pairs so the dedupe demo fires
    for base in random.sample(challenges, 3):
        dup = models.Challenge(
            title=base.title.replace("#", "(reported again) #"),
            description=base.description + " Additional residents have since corroborated this report.",
            domain=base.domain, severity=base.severity, status="SUBMITTED",
            district=base.district, lat=base.lat, lng=base.lng,
            submitted_by_id=users["CITIZEN"].id, ai_confidence=0.8,
            ai_keywords=base.ai_keywords, ai_summary=base.ai_summary,
            beneficiaries_estimate=base.beneficiaries_estimate, created_at=base.created_at + timedelta(days=2),
        )
        db.add(dup)
        db.flush()
        dup.duplicate_of_id = base.id
        challenges.append(dup)
    db.flush()

    print("Seeding 15 proposals, teams, and IP-eligible projects...")
    proposals = []
    validated_challenges = [c for c in challenges if c.status in ("ASSIGNED", "IN_PROGRESS", "PILOT", "IMPLEMENTED", "CLOSED")]
    pool = validated_challenges if len(validated_challenges) >= 15 else challenges
    for i in range(15):
        challenge = pool[i % len(pool)]
        uni = random.choice(universities)
        p = models.Proposal(
            challenge_id=challenge.id, university_id=uni.id,
            title=f"Solution proposal for {challenge.title}",
            approach="Multidisciplinary field study followed by a pilot deployment.",
            methodology="Baseline survey, stakeholder consultation, prototype, field trial, evaluation.",
            expected_outcome="Measurable improvement in the target community outcome within 6 months.",
            budget_estimate=round(random.uniform(50000, 800000), 2), timeline_weeks=random.choice([8, 12, 16, 24]),
            trl_level=random.randint(1, 6), status=random.choice(["SUBMITTED", "APPROVED", "FUNDED"]),
            score=round(random.uniform(50, 95), 1),
        )
        db.add(p)
        proposals.append(p)
    db.flush()

    for p in proposals:
        team = models.Team(proposal_id=p.id, name=f"Team {p.title[:24]}")
        db.add(team)
        db.flush()
        db.add(models.TeamMember(team_id=team.id, user_id=users["FACULTY_MENTOR"].id, role_in_team="Mentor", discipline="Engineering"))
        db.add(models.TeamMember(team_id=team.id, user_id=users["STUDENT"].id, role_in_team="Student Lead", discipline="Engineering"))

    print("Seeding 10 collaborations...")
    for i in range(10):
        p = random.choice(proposals)
        ind = random.choice(industries)
        db.add(models.Collaboration(
            proposal_id=p.id, industry_id=ind.id, type=random.choice(["MENTORSHIP", "FUNDING", "PROTOTYPING", "PILOT", "TECH_TRANSFER"]),
            amount=round(random.uniform(20000, 300000), 2) if random.random() > 0.3 else None,
            status=random.choice(["PROPOSED", "ACTIVE", "COMPLETED"]), notes="Engagement coordinated via Samadhan Setu.",
        ))

    print("Seeding 8 projects with milestones...")
    projects = []
    approved_proposals = [p for p in proposals if p.status in ("APPROVED", "FUNDED")] or proposals
    for i in range(8):
        p = approved_proposals[i % len(approved_proposals)]
        progress = random.randint(10, 100)
        proj = models.Project(
            proposal_id=p.id, status="COMPLETED" if progress >= 100 else "ACTIVE", progress_percent=progress,
            start_date=now - timedelta(days=random.randint(30, 150)), deployment_status=random.choice(["NOT_STARTED", "PILOT", "DEPLOYED"]),
            impact_metrics={"beneficiaries_reached": random.randint(100, 3000), "satisfaction_score": round(random.uniform(3.5, 5.0), 1)},
        )
        db.add(proj)
        db.flush()
        for m_idx, m_title in enumerate(["Baseline survey", "Prototype development", "Field pilot", "Evaluation & handover"]):
            db.add(models.Milestone(
                project_id=proj.id, title=m_title, description=f"{m_title} for project linked to '{p.title[:40]}'.",
                due_date=now + timedelta(days=15 * (m_idx + 1)),
                status=random.choice(["PENDING", "IN_REVIEW", "APPROVED"]), order=m_idx,
            ))
        projects.append(proj)
    db.flush()

    print("Seeding 4 IP records forming a valid hash chain...")
    import hashlib
    import json as jsonlib
    prev_hash = "0" * 64
    for i in range(4):
        proj = projects[i % len(projects)]
        payload = {"project_id": proj.id, "type": "PATENT" if i % 2 == 0 else "COPYRIGHT", "title": f"Innovation output #{i+1}", "app_number": f"JH/2026/{1000+i}", "status": "FILED"}
        ledger_hash = hashlib.sha256((jsonlib.dumps(payload, sort_keys=True) + prev_hash).encode()).hexdigest()
        db.add(models.IPRecord(project_id=proj.id, type=payload["type"], title=payload["title"], app_number=payload["app_number"], status="FILED", ledger_hash=ledger_hash, prev_hash=prev_hash))
        prev_hash = ledger_hash

    print("Seeding comments, upvotes, and notifications...")
    for c in random.sample(challenges, 20):
        db.add(models.Comment(entity_type="challenge", entity_id=c.id, user_id=users["CITIZEN"].id, body="This is a genuine issue in our area — hoping for quick action."))
    for c in random.sample(challenges, 25):
        try:
            db.add(models.Upvote(challenge_id=c.id, user_id=users["COMMUNITY_ORG"].id))
        except Exception:
            pass
    for role in ("CITIZEN", "UNIVERSITY_ADMIN", "GOVT_OFFICIAL", "INDUSTRY_PARTNER"):
        db.add(models.Notification(user_id=users[role].id, title="Welcome to Samadhan Setu", body="Your dashboard has been set up with the latest updates.", type="general"))

    db.commit()
    db.close()

    print("\nSeed complete.")
    print(f"  Users: {len(DEMO_USERS)} | Universities: {len(universities)} | Industries: {len(industries)}")
    print(f"  Challenges: {len(challenges)} | Proposals: {len(proposals)} | Projects: {len(projects)}")
    print("\nDemo logins (password for all: Demo@1234):")
    for name, email, role, *_ in DEMO_USERS:
        print(f"  {role:16s} {email}")


if __name__ == "__main__":
    if "--reset" in sys.argv:
        print("Resetting database...")
        reset_db()
    seed()
