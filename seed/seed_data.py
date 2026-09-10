"""Seed synthetic demo data for PashuRakshak AI.

Run from the repository root:

    python seed/seed_data.py

This is a DEV/DEMO tool only. It fully resets the application tables
(truncating everything, including the users table) and rebuilds a
consistent demo dataset. Never point this at a real deployment -- it
is destructive by design so the SIH demo always starts from a known,
reproducible state.

All data here is synthetic and made up for demonstration purposes. It
must never be treated as real animal health or personal data.
"""

import os
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = REPO_ROOT / "backend"

# pydantic-settings resolves its env_file relative to the process's
# working directory, matching how the backend, alembic, and pytest are
# normally run (from backend/). Do the same here rather than requiring
# the caller to cd first.
os.chdir(BACKEND_DIR)
sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import select, text  # noqa: E402

from app.core.security import hash_password  # noqa: E402
from app.db import base as _models  # noqa: E402, F401  (register all models)
from app.db.session import SessionLocal, engine  # noqa: E402
from app.models.alert import Alert  # noqa: E402
from app.models.animal import Animal  # noqa: E402
from app.models.case import Case  # noqa: E402
from app.models.education import EducationContent  # noqa: E402
from app.models.enums import (  # noqa: E402
    CaseStatus,
    EducationAudience,
    EducationCategory,
    Language,
    Sex,
    Species,
    UserRole,
)
from app.models.farm import Farm, FarmMembership  # noqa: E402
from app.models.user import User  # noqa: E402
from app.schemas.alert import AlertReviewAction  # noqa: E402
from app.schemas.case import CaseClinicalUpdate, CaseCreate  # noqa: E402
from app.schemas.observation import ObservationCreate  # noqa: E402
from app.schemas.vaccination import VaccinationCreate  # noqa: E402
from app.services import alert_service, case_service, observation_service, vaccination_service  # noqa: E402

DEMO_PASSWORD = "Demo@1234"

ALL_TABLES = [
    "case_updates",
    "cases",
    "alerts",
    "risk_assessments",
    "observations",
    "vaccination_records",
    "animals",
    "farm_memberships",
    "farms",
    "education_content",
    "audit_logs",
    "users",
]


def reset_database(db) -> None:
    print("Resetting tables...")
    db.execute(text(f"TRUNCATE TABLE {', '.join(ALL_TABLES)} RESTART IDENTITY CASCADE"))
    db.commit()


def make_user(db, *, name, email, role, language=Language.en) -> User:
    user = User(
        name=name,
        email=email,
        role=role,
        language=language,
        password_hash=hash_password(DEMO_PASSWORD),
    )
    db.add(user)
    db.flush()
    return user


def make_farm(db, *, name, village, district, state, owner: User) -> Farm:
    farm = Farm(name=name, village=village, district=district, state=state)
    db.add(farm)
    db.flush()
    db.add(FarmMembership(farm_id=farm.id, user_id=owner.id, role=owner.role))
    return farm


def make_animal(db, *, farm: Farm, tag_id, species, sex, age_years, breed=None) -> Animal:
    dob = date.today() - timedelta(days=int(age_years * 365.25))
    animal = Animal(farm_id=farm.id, tag_id=tag_id, species=species, sex=sex, dob=dob, breed=breed)
    db.add(animal)
    db.flush()
    return animal


def submit_observation(db, *, animal: Animal, entered_by: User, days_ago: int, **fields):
    observed_at = datetime.now(timezone.utc) - timedelta(days=days_ago)
    payload = ObservationCreate(
        observed_at=observed_at,
        appetite=fields.get("appetite", "normal"),
        activity=fields.get("activity", "normal"),
        water_intake=fields.get("water_intake", "normal"),
        respiratory_sign=fields.get("respiratory_sign", "none"),
        dung_sign=fields.get("dung_sign", "normal"),
        temperature_c=fields.get("temperature_c"),
        milk_yield_change_pct=fields.get("milk_yield_change_pct"),
        notes=fields.get("notes"),
    )
    observation, risk_assessment = observation_service.create_observation(
        db, animal=animal, payload=payload, current_user=entered_by
    )
    return observation, risk_assessment


def get_alert_for_assessment(db, assessment_id: str) -> Alert:
    return db.execute(select(Alert).where(Alert.assessment_id == assessment_id)).scalar_one()


def seed_education_content(db) -> None:
    print("Seeding education content...")
    items = [
        (
            EducationCategory.vaccination,
            "Why vaccinate on schedule",
            "en",
            "Vaccinating on the recommended schedule is one of the most effective ways to "
            "reduce the risk of common preventable diseases in cattle and buffalo. Keep a "
            "written record of every dose given and the next due date.",
            "टीके समय पर क्यों लगवाएं",
            "hi",
            "समय पर टीकाकरण करवाना गाय और भैंस में सामान्य बीमारियों से बचाव का सबसे कारगर "
            "तरीका है। हर टीके की तारीख और अगली तारीख लिखकर रखें।",
        ),
        (
            EducationCategory.hygiene,
            "Clean water troughs weekly",
            "en",
            "Empty and scrub water troughs at least once a week. Dirty, stagnant water is a "
            "common source of infection and can reduce how much an animal drinks.",
            "पानी के बर्तन साप्ताहिक साफ करें",
            "hi",
            "पानी के बर्तन को सप्ताह में कम से कम एक बार खाली करके साफ करें। गंदा पानी बीमारी "
            "फैलने का एक सामान्य कारण है।",
        ),
        (
            EducationCategory.quarantine,
            "Isolate new or sick animals",
            "en",
            "Keep newly purchased animals separate from the herd for at least two weeks, and "
            "isolate any animal showing concerning signs until a veterinarian has reviewed it.",
            "नए या बीमार पशु को अलग रखें",
            "hi",
            "नए खरीदे गए पशु को कम से कम दो हफ्तों तक बाकी पशुओं से अलग रखें, और किसी भी "
            "चिंताजनक पशु को पशु चिकित्सक की जांच तक अलग रखें।",
        ),
        (
            EducationCategory.nutrition,
            "Consistent feeding reduces risk",
            "en",
            "Sudden changes in feed type or quantity can upset digestion. Introduce new feed "
            "gradually over several days and ensure clean drinking water is always available.",
            "नियमित आहार से जोखिम कम होता है",
            "hi",
            "आहार में अचानक बदलाव पाचन बिगाड़ सकता है। नया आहार धीरे-धीरे कई दिनों में शुरू करें "
            "और हमेशा साफ पानी उपलब्ध रखें।",
        ),
        (
            EducationCategory.biosecurity,
            "Limit visitor and vehicle contact",
            "en",
            "Restrict unnecessary visitors and vehicles from entering the animal housing area. "
            "Disinfect footwear when moving between different animal groups.",
            "आगंतुकों और वाहनों का संपर्क सीमित करें",
            "hi",
            "पशुशाला में अनावश्यक आगंतुकों और वाहनों के प्रवेश को सीमित करें। अलग-अलग पशु समूहों "
            "के बीच जाते समय जूते साफ करें।",
        ),
        (
            EducationCategory.general_observation,
            "What to check every day",
            "en",
            "A quick daily check of appetite, activity, breathing, and dung can help you notice "
            "a problem early -- often before it becomes serious.",
            "हर दिन क्या जांचें",
            "hi",
            "भूख, सक्रियता, सांस और गोबर की रोज़ाना जल्दी जांच से समस्या को समय पर पहचानने में "
            "मदद मिलती है, अक्सर गंभीर होने से पहले।",
        ),
    ]

    for category, title_en, lang_en, body_en, title_hi, lang_hi, body_hi in items:
        db.add(
            EducationContent(
                category=category,
                title=title_en,
                language=Language(lang_en),
                body=body_en,
                audience=EducationAudience.farmer,
                is_published=True,
            )
        )
        db.add(
            EducationContent(
                category=category,
                title=title_hi,
                language=Language(lang_hi),
                body=body_hi,
                audience=EducationAudience.farmer,
                is_published=True,
            )
        )
    db.commit()


def main() -> None:
    db = SessionLocal()
    try:
        reset_database(db)

        print("Creating demo users...")
        farmer1 = make_user(db, name="Ramesh Kumar", email="farmer.demo@pashurakshak.ai", role=UserRole.farmer)
        farmer2 = make_user(
            db, name="Sita Devi", email="farmer2.demo@pashurakshak.ai", role=UserRole.farmer, language=Language.hi
        )
        vet1 = make_user(db, name="Dr. Anjali Verma", email="vet.demo@pashurakshak.ai", role=UserRole.veterinarian)
        vet2 = make_user(db, name="Dr. Vikram Singh", email="vet2.demo@pashurakshak.ai", role=UserRole.veterinarian)
        admin = make_user(db, name="System Admin", email="admin.demo@pashurakshak.ai", role=UserRole.admin)
        db.commit()

        print("Creating farms...")
        farm1 = make_farm(
            db, name="Green Valley Farm", village="Rampur", district="Meerut", state="Uttar Pradesh", owner=farmer1
        )
        farm2 = make_farm(
            db, name="Sunrise Dairy Farm", village="Devgaon", district="Nashik", state="Maharashtra", owner=farmer2
        )
        db.commit()

        print("Registering animals...")
        cow_101 = make_animal(
            db, farm=farm1, tag_id="COW-101", species=Species.cattle, sex=Sex.female, age_years=3, breed="Sahiwal"
        )
        cow_102 = make_animal(
            db, farm=farm1, tag_id="COW-102", species=Species.cattle, sex=Sex.female, age_years=5, breed="Gir"
        )
        cow_103 = make_animal(
            db, farm=farm1, tag_id="COW-103", species=Species.cattle, sex=Sex.female, age_years=4, breed="Sahiwal"
        )
        cow_104 = make_animal(
            db, farm=farm1, tag_id="COW-104", species=Species.cattle, sex=Sex.female, age_years=6, breed="Gir"
        )
        buf_101 = make_animal(
            db, farm=farm1, tag_id="BUF-101", species=Species.buffalo, sex=Sex.female, age_years=4, breed="Murrah"
        )
        buf_102 = make_animal(
            db, farm=farm1, tag_id="BUF-102", species=Species.buffalo, sex=Sex.female, age_years=3, breed="Murrah"
        )
        cow_201 = make_animal(
            db, farm=farm2, tag_id="COW-201", species=Species.cattle, sex=Sex.female, age_years=2, breed="Jersey"
        )
        cow_202 = make_animal(
            db, farm=farm2, tag_id="COW-202", species=Species.cattle, sex=Sex.female, age_years=3, breed="HF Cross"
        )
        cow_203 = make_animal(
            db, farm=farm2, tag_id="COW-203", species=Species.cattle, sex=Sex.female, age_years=5, breed="Jersey"
        )
        buf_201 = make_animal(
            db, farm=farm2, tag_id="BUF-201", species=Species.buffalo, sex=Sex.male, age_years=1, breed="Murrah"
        )
        buf_202 = make_animal(
            db, farm=farm2, tag_id="BUF-202", species=Species.buffalo, sex=Sex.female, age_years=2, breed="Murrah"
        )
        db.commit()

        print("Submitting observation history...")
        # COW-101: healthy history, then a HIGH-risk observation today --
        # the primary "today's alert" for the SIH demo walkthrough.
        for days_ago in (6, 4, 2):
            submit_observation(db, animal=cow_101, entered_by=farmer1, days_ago=days_ago)
        submit_observation(
            db,
            animal=cow_101,
            entered_by=farmer1,
            days_ago=0,
            appetite="none",
            activity="lethargic",
            water_intake="reduced",
            respiratory_sign="labored",
            dung_sign="bloody",
            temperature_c=41.0,
            milk_yield_change_pct=-55,
            notes="Found lying down in the shade, did not come for feeding.",
        )

        # COW-102: consistently healthy -- a normal-looking demo animal.
        for days_ago in (7, 5, 3, 1):
            submit_observation(db, animal=cow_102, entered_by=farmer1, days_ago=days_ago)

        # BUF-101: a MEDIUM-risk observation today.
        for days_ago in (5, 3):
            submit_observation(db, animal=buf_101, entered_by=farmer1, days_ago=days_ago)
        submit_observation(
            db,
            animal=buf_101,
            entered_by=farmer1,
            days_ago=0,
            appetite="reduced",
            activity="normal",
            respiratory_sign="mild",
            dung_sign="normal",
            temperature_c=None,
            milk_yield_change_pct=-10,
            notes="Slightly less feed intake since yesterday.",
        )

        # Healthy background herd -- rounds out both farms to a realistic
        # size without generating extra alerts.
        for days_ago in (5, 2):
            submit_observation(db, animal=buf_102, entered_by=farmer1, days_ago=days_ago)
        for days_ago in (4, 2):
            submit_observation(db, animal=cow_201, entered_by=farmer2, days_ago=days_ago)
        for days_ago in (6, 3):
            submit_observation(db, animal=cow_202, entered_by=farmer2, days_ago=days_ago)
        for days_ago in (5, 2):
            submit_observation(db, animal=buf_202, entered_by=farmer2, days_ago=days_ago)

        # BUF-201: a MEDIUM alert from two days ago, escalated to a
        # follow-up and then resolved with a vet-confirmed outcome --
        # populates a "resolved" case and "recently reviewed" on the vet
        # dashboard.
        _obs, buf_201_assessment = submit_observation(
            db,
            animal=buf_201,
            entered_by=farmer2,
            days_ago=2,
            appetite="reduced",
            activity="normal",
            respiratory_sign="none",
            dung_sign="loose",
        )

        # COW-203: a MEDIUM alert from yesterday, escalated to a follow-up
        # that is still awaiting the vet's next visit -- populates a
        # "follow_up" case.
        _obs, cow_203_assessment = submit_observation(
            db,
            animal=cow_203,
            entered_by=farmer2,
            days_ago=1,
            appetite="reduced",
            activity="normal",
            water_intake="normal",
            respiratory_sign="mild",
            dung_sign="normal",
            milk_yield_change_pct=-8,
            notes="Eating a little less since yesterday evening.",
        )
        db.commit()

        print("Setting up example cases in each workflow state...")

        # 1. "resolved": acknowledge -> request follow-up -> vet confirms
        #    a clinical outcome and closes the case.
        buf_201_alert = get_alert_for_assessment(db, buf_201_assessment.id)
        alert_service.apply_review_action(
            db, alert=buf_201_alert, action=AlertReviewAction(action="acknowledge"), current_user=vet1
        )
        alert_service.apply_review_action(
            db,
            alert=buf_201_alert,
            action=AlertReviewAction(
                action="request_follow_up",
                note="Scheduling an on-farm check for suspected mild indigestion.",
                follow_up_at=datetime.now(timezone.utc) - timedelta(days=1),
            ),
            current_user=vet1,
        )
        buf_201_case = db.execute(select(Case).where(Case.alert_id == buf_201_alert.id)).scalar_one()
        case_service.update_case_clinical(
            db,
            case=buf_201_case,
            payload=CaseClinicalUpdate(
                status=CaseStatus.resolved,
                confirmed_condition="Mild indigestion",
                confirmation_basis="On-farm physical exam by Dr. Anjali Verma; resolved without treatment.",
            ),
            current_user=vet1,
        )
        alert_service.apply_review_action(
            db,
            alert=buf_201_alert,
            action=AlertReviewAction(
                action="resolve", note="On-farm check: mild indigestion, resolved without treatment."
            ),
            current_user=vet1,
        )

        # 2. "follow_up": acknowledge -> request follow-up, left open for
        #    the vet's next scheduled visit.
        cow_203_alert = get_alert_for_assessment(db, cow_203_assessment.id)
        alert_service.apply_review_action(
            db, alert=cow_203_alert, action=AlertReviewAction(action="acknowledge"), current_user=vet2
        )
        alert_service.apply_review_action(
            db,
            alert=cow_203_alert,
            action=AlertReviewAction(
                action="request_follow_up",
                note="Reduced appetite and mild feed drop -- recheck at next visit.",
                follow_up_at=datetime.now(timezone.utc) + timedelta(days=2),
            ),
            current_user=vet2,
        )

        # 3. "open": a case opened directly by a vet from a physical visit,
        #    not tied to an AI alert.
        case_service.open_case(
            db,
            animal=cow_103,
            payload=CaseCreate(suspected_condition="Suspected mild respiratory infection"),
            current_user=vet1,
        )

        # 4. "under_review": opened, then moved into active clinical review.
        cow_104_case = case_service.open_case(
            db,
            animal=cow_104,
            payload=CaseCreate(suspected_condition="Suspected early-stage mastitis"),
            current_user=vet1,
        )
        case_service.update_case_clinical(
            db,
            case=cow_104_case,
            payload=CaseClinicalUpdate(status=CaseStatus.under_review),
            current_user=vet1,
        )

        print("Adding vaccination records...")
        vaccination_service.create_vaccination_record(
            db,
            animal=cow_101,
            payload=VaccinationCreate(
                vaccine_name="FMD (Foot-and-Mouth Disease)",
                dose_date=date.today() - timedelta(days=120),
                due_date=date.today() + timedelta(days=10),
            ),
            current_user=vet1,
        )
        vaccination_service.create_vaccination_record(
            db,
            animal=cow_102,
            payload=VaccinationCreate(
                vaccine_name="Brucellosis",
                due_date=date.today() - timedelta(days=5),
            ),
            current_user=vet1,
        )
        vaccination_service.create_vaccination_record(
            db,
            animal=buf_101,
            payload=VaccinationCreate(
                vaccine_name="HS (Haemorrhagic Septicaemia)",
                dose_date=date.today() - timedelta(days=30),
            ),
            current_user=vet1,
        )
        vaccination_service.create_vaccination_record(
            db,
            animal=cow_201,
            payload=VaccinationCreate(
                vaccine_name="FMD (Foot-and-Mouth Disease)",
                due_date=date.today() + timedelta(days=20),
            ),
            current_user=vet2,
        )
        vaccination_service.create_vaccination_record(
            db,
            animal=cow_103,
            payload=VaccinationCreate(
                vaccine_name="HS (Haemorrhagic Septicaemia)",
                due_date=date.today() + timedelta(days=3),
            ),
            current_user=vet1,
        )
        vaccination_service.create_vaccination_record(
            db,
            animal=buf_202,
            payload=VaccinationCreate(
                vaccine_name="Brucellosis",
                dose_date=date.today() - timedelta(days=200),
                due_date=date.today() - timedelta(days=2),
            ),
            current_user=vet2,
        )
        db.commit()

        seed_education_content(db)

        print("\nDone. Demo accounts (password for all: Demo@1234):")
        for user in (farmer1, farmer2, vet1, vet2, admin):
            print(f"  {user.role.value:<13} {user.email}")

    finally:
        db.close()
        engine.dispose()


if __name__ == "__main__":
    main()
