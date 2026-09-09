import os

os.environ["ENVIRONMENT"] = "test"
os.environ["DATABASE_URL"] = (
    "postgresql+psycopg://pashurakshak:pashurakshak_dev_pw@localhost:5432/pashurakshak_test"
)
os.environ["JWT_SECRET_KEY"] = "test-secret-key-not-for-production-use-only"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine, text  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

import app.db.base as db_base  # noqa: E402, F401  (register all models)
from app.api.deps import get_db  # noqa: E402
from app.core.config import get_settings  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.main import app  # noqa: E402
from app.models.animal import Animal  # noqa: E402
from app.models.enums import Language, Sex, Species, UserRole  # noqa: E402
from app.models.farm import Farm, FarmMembership  # noqa: E402
from app.models.user import User  # noqa: E402

settings = get_settings()
engine = create_engine(settings.DATABASE_URL, future=True)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)

_ALL_TABLES = [
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


@pytest.fixture(autouse=True)
def _clean_db():
    """Truncate every table before each test so tests stay independent."""
    with engine.begin() as conn:
        conn.execute(text(f"TRUNCATE TABLE {', '.join(_ALL_TABLES)} RESTART IDENTITY CASCADE"))
    yield


@pytest.fixture
def db():
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db):
    def _override_get_db():
        yield db

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def make_user(db, *, role, email=None, phone=None, password="testpass123", name="Test User"):
    user = User(
        name=name,
        email=email,
        phone=phone,
        role=role,
        language=Language.en,
        password_hash=hash_password(password),
    )
    db.add(user)
    db.commit()
    return user


@pytest.fixture
def farmer_user(db):
    return make_user(db, role=UserRole.farmer, email="farmer@example.com")


@pytest.fixture
def vet_user(db):
    return make_user(db, role=UserRole.veterinarian, email="vet@example.com")


@pytest.fixture
def admin_user(db):
    return make_user(db, role=UserRole.admin, email="admin@example.com")


def auth_header(client, email, password="testpass123"):
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def farm(db, farmer_user):
    farm = Farm(name="Green Valley Farm", village="Rampur", district="Meerut", state="UP")
    db.add(farm)
    db.flush()
    db.add(FarmMembership(farm_id=farm.id, user_id=farmer_user.id, role=UserRole.farmer))
    db.commit()
    return farm


@pytest.fixture
def other_farm(db):
    other_farmer = make_user(
        db, role=UserRole.farmer, email="other_farmer@example.com", name="Other Farmer"
    )
    farm = Farm(name="Other Farm", village="Elsewhere")
    db.add(farm)
    db.flush()
    db.add(FarmMembership(farm_id=farm.id, user_id=other_farmer.id, role=UserRole.farmer))
    db.commit()
    return farm


@pytest.fixture
def animal(db, farm):
    animal = Animal(farm_id=farm.id, tag_id="COW-001", species=Species.cattle, sex=Sex.female)
    db.add(animal)
    db.commit()
    return animal
