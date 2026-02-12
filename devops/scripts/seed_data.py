"""
Alfred Seed Data Script
Generates realistic demo data for the dashboard.
Run with: python -m scripts.seed_data
"""

import sys
import io
import random
import hashlib
import secrets
from datetime import datetime, timedelta
from decimal import Decimal
import uuid

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from sqlmodel import Session, SQLModel, create_engine, select
from app.models import (
    User, Team, TeamMemberLink, RequestLog, LeaderboardEntry,
    OrgSettings, ApprovalRequest, TokenTransfer,
    UserStatus, ProjectPriority
)
from app.config import settings


def generate_api_key() -> tuple[str, str]:
    """Generate API key and its hash."""
    key = f"{settings.api_key_prefix}{secrets.token_urlsafe(settings.api_key_length)}"
    hash_obj = hashlib.sha256(key.encode())
    return key, hash_obj.hexdigest()


def seed_database(session: Session, verbose: bool = True):
    """Seed the database with demo data."""
    
    # Check if already seeded
    existing_users = session.exec(select(User)).first()
    if existing_users:
        if verbose:
            print("Database already has data. Skipping seed.")
        return
    
    print("🌱 Seeding database with demo data...")
    
    # Create OrgSettings if not exists
    org_settings = session.exec(select(OrgSettings)).first()
    if not org_settings:
        org_settings = OrgSettings()
        session.add(org_settings)
    
    # --- Create Teams ---
    teams_data = [
        {"name": "Engineering", "description": "Software development team", "common_pool": Decimal("50000.00")},
        {"name": "Data Science", "description": "ML and analytics team", "common_pool": Decimal("75000.00")},
        {"name": "Marketing", "description": "Content and marketing team", "common_pool": Decimal("25000.00")},
        {"name": "Product", "description": "Product management team", "common_pool": Decimal("30000.00")},
        {"name": "Support", "description": "Customer support team", "common_pool": Decimal("20000.00")},
    ]
    
    teams = []
    for td in teams_data:
        team = Team(
            name=td["name"],
            description=td["description"],
            common_pool=td["common_pool"],
            used_pool=Decimal(str(random.uniform(0.3, 0.7))) * td["common_pool"]
        )
        session.add(team)
        teams.append(team)
    
    session.flush()
    print(f"  ✓ Created {len(teams)} teams")
    
    # --- Create Users ---
    users_data = [
        {"name": "Alice Johnson", "email": "alice.johnson@company.com", "quota": 5000, "is_admin": True},
        {"name": "Bob Smith", "email": "bob.smith@company.com", "quota": 3000, "is_admin": False},
        {"name": "Carol Williams", "email": "carol.williams@company.com", "quota": 4000, "is_admin": False},
        {"name": "David Brown", "email": "david.brown@company.com", "quota": 2500, "is_admin": False},
        {"name": "Eve Davis", "email": "eve.davis@company.com", "quota": 3500, "is_admin": False},
        {"name": "Frank Miller", "email": "frank.miller@company.com", "quota": 2000, "is_admin": False},
        {"name": "Grace Lee", "email": "grace.lee@company.com", "quota": 4500, "is_admin": True},
        {"name": "Henry Wilson", "email": "henry.wilson@company.com", "quota": 3000, "is_admin": False},
        {"name": "Ivy Chen", "email": "ivy.chen@company.com", "quota": 5000, "is_admin": False},
        {"name": "Jack Taylor", "email": "jack.taylor@company.com", "quota": 2500, "is_admin": False},
        {"name": "Kate Anderson", "email": "kate.anderson@company.com", "quota": 3500, "is_admin": False},
        {"name": "Leo Martinez", "email": "leo.martinez@company.com", "quota": 4000, "is_admin": False},
        {"name": "Maria Garcia", "email": "maria.garcia@company.com", "quota": 3000, "is_admin": False},
        {"name": "Nathan White", "email": "nathan.white@company.com", "quota": 2000, "is_admin": False},
        {"name": "Olivia Harris", "email": "olivia.harris@company.com", "quota": 3500, "is_admin": False},
    ]
    
    admin_api_key = None  # Store for output
    users = []
    
    for ud in users_data:
        api_key, api_key_hash = generate_api_key()
        used = Decimal(str(random.uniform(0.2, 0.85))) * Decimal(str(ud["quota"]))
        
        user = User(
            name=ud["name"],
            email=ud["email"],
            api_key_hash=api_key_hash,
            personal_quota=Decimal(str(ud["quota"])),
            used_tokens=used,
            is_admin=ud["is_admin"],
            status=random.choice([UserStatus.ACTIVE, UserStatus.ACTIVE, UserStatus.ACTIVE, UserStatus.ON_VACATION]),
            default_priority=ProjectPriority.NORMAL
        )
        session.add(user)
        users.append(user)
        
        if ud["is_admin"] and not admin_api_key:
            admin_api_key = api_key
    
    session.flush()
    print(f"  ✓ Created {len(users)} users")
    
    # --- Assign users to teams ---
    team_assignments = [
        (0, [0, 1, 2, 3]),      # Engineering: Alice, Bob, Carol, David
        (1, [4, 5, 8, 11]),     # Data Science: Eve, Frank, Ivy, Leo
        (2, [6, 7, 12]),        # Marketing: Grace, Henry, Maria
        (3, [9, 10]),           # Product: Jack, Kate
        (4, [13, 14]),          # Support: Nathan, Olivia
    ]
    
    for team_idx, user_indices in team_assignments:
        for user_idx in user_indices:
            link = TeamMemberLink(
                team_id=teams[team_idx].id,
                user_id=users[user_idx].id,
                is_admin=(user_idx == user_indices[0])  # First user is team admin
            )
            session.add(link)
    
    session.flush()
    print("  ✓ Assigned users to teams")
    
    # --- Create Request Logs (last 30 days) ---
    models = [
        ("gpt-4o", "openai"),
        ("gpt-4-turbo", "openai"),
        ("gpt-3.5-turbo", "openai"),
        ("claude-3-opus-20240229", "anthropic"),
        ("claude-3-sonnet-20240229", "anthropic"),
        ("claude-3-haiku-20240307", "anthropic"),
        ("gemini-1.5-pro", "google"),
    ]
    
    request_count = 0
    for days_ago in range(30, -1, -1):
        date = datetime.utcnow() - timedelta(days=days_ago)
        daily_requests = random.randint(50, 200)
        
        for _ in range(daily_requests):
            user = random.choice(users)
            model, provider = random.choice(models)
            
            prompt_tokens = random.randint(100, 2000)
            completion_tokens = random.randint(50, 1500)
            total_tokens = prompt_tokens + completion_tokens
            
            # Estimate cost based on model
            if "gpt-4" in model:
                cost_per_1k = Decimal("0.03")
            elif "claude-3-opus" in model:
                cost_per_1k = Decimal("0.015")
            elif "claude-3-sonnet" in model:
                cost_per_1k = Decimal("0.003")
            else:
                cost_per_1k = Decimal("0.002")
            
            cost = (Decimal(total_tokens) / Decimal("1000")) * cost_per_1k * Decimal("100")
            
            log = RequestLog(
                user_id=user.id,
                model=model,
                provider=provider,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                cost_credits=cost,
                strict_privacy=random.choice([False, False, False, True]),
                priority=random.choice([ProjectPriority.NORMAL, ProjectPriority.NORMAL, ProjectPriority.HIGH]),
                quota_source=random.choice(["personal", "personal", "team_pool", "vacation_share"]),
                created_at=date + timedelta(
                    hours=random.randint(8, 20),
                    minutes=random.randint(0, 59)
                )
            )
            session.add(log)
            request_count += 1
    
    session.flush()
    print(f"  ✓ Created {request_count} request logs")
    
    # --- Create Leaderboard Entries ---
    for user in users:
        entry = LeaderboardEntry(
            user_id=user.id,
            period_start=datetime.utcnow() - timedelta(days=7),
            period_end=datetime.utcnow(),
            period_type="weekly",
            total_requests=random.randint(50, 500),
            total_prompt_tokens=random.randint(10000, 100000),
            total_completion_tokens=random.randint(5000, 50000),
            efficiency_score=Decimal(str(random.uniform(0.6, 0.98))),
            rank=0  # Will be calculated
        )
        session.add(entry)
    
    session.flush()
    print("  ✓ Created leaderboard entries")
    
    # --- Create Approval Requests ---
    statuses = ["pending", "approved", "approved", "rejected"]
    for _ in range(15):
        user = random.choice(users)
        created = datetime.utcnow() - timedelta(days=random.randint(0, 14))
        status = random.choice(statuses)
        
        approval = ApprovalRequest(
            user_id=user.id,
            requested_credits=Decimal(str(random.randint(500, 5000))),
            reason=random.choice([
                "Large research project",
                "Production deployment support",
                "Customer demo preparation",
                "Quarterly report generation",
                "Training data preparation"
            ]),
            status=status,
            created_at=created,
            resolved_at=created + timedelta(hours=random.randint(1, 48)) if status != "pending" else None,
            resolved_by_id=random.choice([u.id for u in users if u.is_admin]) if status != "pending" else None
        )
        session.add(approval)
    
    session.flush()
    print("  ✓ Created approval requests")
    
    # --- Create Credit Reallocations ---
    for _ in range(20):
        from_user, to_user = random.sample(users, 2)
        
        transfer = TokenTransfer(
            sender_id=from_user.id,
            recipient_id=to_user.id,
            amount=Decimal(str(random.randint(100, 1000))),
            message=random.choice([
                "Project capacity needs",
                "Sprint deadline support",
                "Team capacity rebalancing",
                "Cross-team collaboration",
                "Project handoff"
            ]),
            created_at=datetime.utcnow() - timedelta(days=random.randint(0, 30))
        )
        session.add(transfer)
    
    session.commit()
    print("  ✓ Created credit reallocations")
    
    print("\n✅ Database seeded successfully!")
    print(f"\n🔑 Admin API Key (save this!):\n   {admin_api_key}")
    print(f"\n   Admin User: {users[0].name} ({users[0].email})")
    
    return admin_api_key


if __name__ == "__main__":
    # Create engine
    connect_args = {"check_same_thread": False} if settings.is_sqlite else {}
    engine = create_engine(
        settings.database_url,
        echo=False,
        connect_args=connect_args
    )
    
    # Ensure tables exist
    SQLModel.metadata.create_all(engine)
    
    # Seed data
    with Session(engine) as session:
        seed_database(session)
