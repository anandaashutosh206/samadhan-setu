"""
Generates api/app/ai/data/train_challenges.json — a labelled corpus of
realistic Jharkhand-context societal challenge reports across the 10 domains,
each with a domain label and a severity label. Deterministic (seeded) so the
corpus is reproducible. Run: python generate_corpus.py
"""
import itertools
import json
import random
from pathlib import Path

random.seed(42)

DISTRICTS = [
    "Ranchi", "Dhanbad", "East Singhbhum", "West Singhbhum", "Bokaro", "Deoghar",
    "Hazaribagh", "Giridih", "Palamu", "Garhwa", "Gumla", "Simdega", "Khunti",
    "Lohardaga", "Ramgarh", "Chatra", "Koderma", "Godda", "Sahibganj", "Pakur",
    "Dumka", "Jamtara", "Latehar", "Seraikela Kharsawan",
]

# domain -> list of (title_template, description_template, severity_pool)
TEMPLATES: dict[str, list[tuple[str, str, list[str]]]] = {
    "education": [
        ("Government school in {district} has no functioning toilets",
         "The government middle school in {district} district has broken or non-functional toilets, forcing girl students to skip classes during menstruation. Parents have complained to the block education officer multiple times with no repair carried out this academic year.",
         ["high", "critical"]),
        ("Shortage of subject teachers in {district} secondary schools",
         "Several secondary schools in {district} are running without science and mathematics teachers for over six months, affecting board exam preparation for class 10 and 12 students in the block.",
         ["high", "medium"]),
        ("No digital classroom or computer lab in village school, {district}",
         "The upgraded high school in a remote village of {district} received a computer lab grant two years ago but computers were never installed, leaving students without any digital literacy exposure.",
         ["medium", "low"]),
        ("Mid-day meal quality complaints from school in {district}",
         "Parents in {district} report that mid-day meals served at the primary school are frequently substandard, sometimes stale, raising health concerns for young children.",
         ["medium", "high"]),
        ("High dropout rate among tribal girl students in {district}",
         "Local NGOs report rising dropout of adolescent tribal girls after class 8 in {district} due to distance to secondary schools and lack of hostel facilities.",
         ["high", "critical"]),
        ("Library and reading resources absent in block schools, {district}",
         "Most upper primary schools in {district} block lack a functioning library or age-appropriate reading material, limiting literacy development beyond textbooks.",
         ["low", "medium"]),
    ],
    "agriculture": [
        ("Crop damage due to erratic rainfall in {district}",
         "Paddy farmers in {district} report significant crop loss this kharif season due to delayed monsoon followed by sudden heavy rainfall, with no crop insurance claims processed yet.",
         ["high", "critical"]),
        ("Farmers in {district} lack access to soil testing labs",
         "Smallholder farmers in {district} district have to travel over 40 km to the nearest soil testing facility, leading to inefficient fertilizer use and declining yields.",
         ["medium", "low"]),
        ("Post-harvest storage loss for vegetable farmers, {district}",
         "Vegetable growers in {district} lose up to 25% of produce due to lack of cold storage and poor rural roads connecting farms to the local mandi.",
         ["high", "medium"]),
        ("Irrigation canal siltation affecting farmland in {district}",
         "A key minor irrigation canal serving several villages in {district} has not been desilted in years, cutting off water supply to nearly 200 acres of cultivable land.",
         ["high", "critical"]),
        ("Low adoption of improved seed varieties in {district}",
         "Farmers in remote blocks of {district} continue using traditional low-yield paddy seed varieties due to lack of awareness and unavailability of certified seeds from Krishi Vigyan Kendra.",
         ["medium", "low"]),
        ("Human-wildlife conflict damaging crops near forest fringe, {district}",
         "Elephant herds from nearby forest areas in {district} have repeatedly damaged standing crops of maize and paddy near forest-fringe villages, with no compensation disbursed.",
         ["high", "medium"]),
    ],
    "healthcare": [
        ("Primary health centre in {district} lacks doctor and medicines",
         "The primary health centre serving multiple panchayats in {district} has been without a resident doctor for over a year, and essential medicines are frequently out of stock.",
         ["critical", "high"]),
        ("High maternal mortality reported in remote blocks of {district}",
         "Community health workers in {district} flag a rise in home deliveries without skilled attendance due to the nearest functional delivery point being over 20 km away.",
         ["critical", "high"]),
        ("Malnutrition among children in Anganwadi centres, {district}",
         "Anganwadi records from {district} show a significant proportion of children under five classified as underweight, with irregular supplementary nutrition supply.",
         ["critical", "high"]),
        ("Lack of ambulance service in interior villages of {district}",
         "Villagers in interior parts of {district} report having no access to ambulance services during medical emergencies, often relying on private vehicles or bullock carts.",
         ["high", "critical"]),
        ("Rising waterborne disease cases during monsoon in {district}",
         "Local health workers in {district} report a spike in diarrhoea and typhoid cases each monsoon linked to contaminated drinking water sources in nearby hamlets.",
         ["high", "medium"]),
        ("Mental health services absent at district hospital, {district}",
         "The district hospital in {district} has no dedicated mental health counsellor or psychiatrist, leaving patients with no local access to care.",
         ["medium", "high"]),
    ],
    "water_resources": [
        ("Drinking water scarcity in summer months, {district}",
         "Several hamlets in {district} face acute drinking water shortage every summer as hand pumps run dry, forcing women to walk over 3 km daily to fetch water.",
         ["critical", "high"]),
        ("Groundwater contamination with iron reported in {district}",
         "Water quality tests in parts of {district} show excess iron content in groundwater, making it unfit for regular consumption without treatment.",
         ["high", "medium"]),
        ("Non-functional piped water scheme in village, {district}",
         "A Jal Jeevan Mission piped water connection scheme in {district} village remains non-functional a year after installation due to pump motor failure.",
         ["high", "critical"]),
        ("Pond and check dam desilting needed in {district}",
         "Traditional water bodies in {district} that recharge the local aquifer have silted up over the years, reducing available water for both irrigation and drinking.",
         ["medium", "low"]),
        ("Fluoride contamination affecting bone health in {district}",
         "Residents in pockets of {district} show early signs of skeletal fluorosis linked to high fluoride content in the only available borewell water source.",
         ["critical", "high"]),
    ],
    "environment": [
        ("Illegal sand mining damaging riverbank in {district}",
         "Unregulated sand mining along the river in {district} is causing riverbank erosion and threatening nearby agricultural land and a village road.",
         ["high", "critical"]),
        ("Uncollected solid waste piling up in {district} town",
         "Municipal solid waste in a ward of {district} town remains uncollected for days at a time, leading to foul smell, stray animal menace, and breeding grounds for mosquitoes.",
         ["medium", "high"]),
        ("Deforestation near coal mining belt in {district}",
         "Local environmental groups report accelerating deforestation around the coal mining belt in {district}, affecting the microclimate and traditional forest-based livelihoods.",
         ["high", "critical"]),
        ("Air quality deterioration near industrial cluster, {district}",
         "Residents living near the industrial cluster in {district} report worsening air quality with visible dust and smoke, correlating with rising respiratory complaints.",
         ["high", "medium"]),
        ("Plastic waste choking drainage channels in {district}",
         "Improper plastic waste disposal is clogging natural drainage channels in {district}, causing waterlogging during even moderate rainfall.",
         ["medium", "low"]),
    ],
    "energy": [
        ("Frequent power outages disrupting daily life in {district}",
         "Villages in {district} experience power cuts lasting 8-10 hours daily, disrupting small businesses, cold storage of produce, and children's evening study time.",
         ["high", "medium"]),
        ("Unelectrified hamlets remain off-grid in {district}",
         "Several small hamlets in the interior of {district} remain without any grid electricity connection despite being listed as electrified under national schemes.",
         ["critical", "high"]),
        ("Low uptake of solar micro-grids in remote {district} villages",
         "Remote villages in {district} that are not economically viable for grid extension have seen little uptake of solar micro-grid alternatives due to lack of awareness and financing options.",
         ["medium", "low"]),
        ("Damaged transformers not replaced for months in {district}",
         "A burnt distribution transformer serving multiple villages in {district} has not been replaced for several months, leaving hundreds of households without power.",
         ["high", "critical"]),
    ],
    "urban_development": [
        ("Poor drainage causing waterlogging in {district} town wards",
         "Several low-lying wards of {district} town flood with even moderate rainfall due to inadequate and poorly maintained drainage infrastructure.",
         ["high", "medium"]),
        ("Unplanned urban growth straining civic amenities in {district}",
         "Rapid unplanned settlement expansion on the outskirts of {district} town has outpaced water supply, sewage, and road infrastructure planning.",
         ["medium", "high"]),
        ("Street lighting absent in newly developed colony, {district}",
         "A newly developed residential colony in {district} town lacks street lighting, raising safety concerns for women and the elderly after dark.",
         ["medium", "low"]),
        ("Encroachment on public land and footpaths in {district}",
         "Vendor and structure encroachment on footpaths in the main market area of {district} town has made pedestrian movement unsafe, especially for the elderly and disabled.",
         ["low", "medium"]),
        ("Poor solid waste segregation infrastructure in {district} municipality",
         "The {district} municipal area lacks door-to-door segregated waste collection, with most waste going untreated to an overflowing dump yard.",
         ["medium", "high"]),
    ],
    "accessibility": [
        ("Government buildings in {district} lack wheelchair access",
         "Several government offices in {district} including the block development office have no ramps or accessible toilets, making it difficult for persons with disabilities to access services.",
         ["high", "medium"]),
        ("No sign language interpreters at public service counters, {district}",
         "Public service delivery counters in {district} including the district hospital have no sign language support, excluding hearing-impaired citizens from timely service.",
         ["medium", "high"]),
        ("Public transport inaccessible for persons with disabilities in {district}",
         "Buses and shared transport operating in {district} are not equipped for wheelchair users, limiting mobility and access to healthcare and education for disabled residents.",
         ["medium", "high"]),
        ("Braille and assistive learning material unavailable in {district} schools",
         "Schools with visually impaired students in {district} report a lack of Braille textbooks and assistive learning devices, affecting inclusive education goals.",
         ["high", "medium"]),
    ],
    "public_administration": [
        ("Long delays in caste and income certificate issuance, {district}",
         "Citizens in {district} report waiting several months for caste and income certificates from the block office, delaying access to scholarships and welfare schemes.",
         ["medium", "high"]),
        ("Land record digitisation errors causing disputes in {district}",
         "Digitised land records in parts of {district} contain mismatches with physical records, leading to an increase in ownership disputes and loan rejections for farmers.",
         ["medium", "high"]),
        ("Poor grievance redressal at panchayat level in {district}",
         "Villagers in {district} report that grievances submitted at the gram panchayat level rarely receive a documented response or resolution timeline.",
         ["medium", "low"]),
        ("Pension disbursement delays for elderly citizens in {district}",
         "Elderly beneficiaries of the old-age pension scheme in {district} report irregular and delayed monthly disbursement, affecting their basic subsistence.",
         ["high", "medium"]),
        ("Ration card corrections stuck in bureaucratic delay, {district}",
         "Numerous ration card correction and addition requests in {district} remain pending for over a year, affecting food security for eligible households.",
         ["medium", "high"]),
    ],
    "rural_livelihoods": [
        ("MGNREGA wage payment delays affecting rural households in {district}",
         "Rural households in {district} enrolled under MGNREGA report wage payment delays of several weeks to months, forcing many to migrate for daily wage work.",
         ["high", "critical"]),
        ("Lack of market linkage for tribal forest produce in {district}",
         "Tribal collectors of minor forest produce like mahua and tendu leaves in {district} continue to sell to middlemen at low prices due to absence of organised market linkage or processing units.",
         ["medium", "high"]),
        ("Seasonal distress migration from {district} villages",
         "Every year, a large number of working-age villagers from {district} migrate to other states for construction and brick-kiln work due to lack of local livelihood opportunities.",
         ["high", "critical"]),
        ("Self-help groups in {district} lack access to formal credit",
         "Women-led self-help groups in {district} report difficulty accessing bank credit for scaling up small enterprises despite consistent savings track records.",
         ["medium", "low"]),
        ("Handicraft artisans in {district} lack design and market support",
         "Traditional bamboo and lac handicraft artisans in {district} face declining incomes due to lack of design innovation support and direct market access, relying entirely on local haats.",
         ["medium", "low"]),
    ],
}


def build_corpus() -> list[dict]:
    rows: list[dict] = []
    combos = list(itertools.product(TEMPLATES.keys(), range(len(DISTRICTS))))
    random.shuffle(combos)

    for domain, templates in TEMPLATES.items():
        # Cycle through districts so every template gets several district variants
        for t_idx, (title_t, desc_t, sev_pool) in enumerate(templates):
            for d_idx, district in enumerate(DISTRICTS):
                # Not every template x district combo — sample to keep corpus balanced,
                # but guarantee at least ~6 examples per template (>=300 total overall).
                if (d_idx + t_idx) % 4 != 0:
                    continue
                severity = sev_pool[(d_idx + t_idx) % len(sev_pool)]
                rows.append(
                    {
                        "title": title_t.format(district=district),
                        "description": desc_t.format(district=district),
                        "domain": domain,
                        "severity": severity,
                        "district": district,
                    }
                )

    random.shuffle(rows)
    return rows


if __name__ == "__main__":
    corpus = build_corpus()
    out_path = Path(__file__).parent / "train_challenges.json"
    out_path.write_text(json.dumps(corpus, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(corpus)} labelled examples to {out_path}")
    by_domain: dict[str, int] = {}
    for r in corpus:
        by_domain[r["domain"]] = by_domain.get(r["domain"], 0) + 1
    for k, v in sorted(by_domain.items()):
        print(f"  {k:25s} {v}")
