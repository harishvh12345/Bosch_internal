import asyncio
import logging
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings
from app.database.base_class import Base
from app.models.user import Role, Department, User
from app.models.profile import UserProfile, Skill, ProfileSkill
from app.models.simulation import Simulation
from app.core.security import security_service

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init_db():
    logger.info("Connecting to database and creating tables...")
    
    # We use a temporary synchronous engine check if we want to create DB, 
    # but SQLAlchemy's create_all works perfectly on async engines via run_sync.
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    
    async with engine.begin() as conn:
        # Create all tables in database
        await conn.run_sync(Base.metadata.create_all)
        
    logger.info("Tables created successfully.")
    
    # Initialize session factory
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import sessionmaker
    
    AsyncSessionLocal = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with AsyncSessionLocal() as db:
        # 1. Seed Roles
        logger.info("Seeding roles...")
        roles = ["Admin", "Manager", "Employee"]
        role_objs = {}
        for r_name in roles:
            from sqlalchemy import select
            res = await db.execute(select(Role).where(Role.name == r_name))
            role = res.scalar_one_or_none()
            if not role:
                role = Role(name=r_name)
                db.add(role)
                await db.flush()
            role_objs[r_name] = role

        # 2. Seed Departments
        logger.info("Seeding departments...")
        depts = [
            ("Embedded Powertrain Systems", "EPS"),
            ("Chassis Systems Control", "CC"),
            ("Connected Mobility Solutions", "MS"),
            ("Information Technology", "IT")
        ]
        dept_objs = {}
        for name, code in depts:
            res = await db.execute(select(Department).where(Department.code == code))
            dept = res.scalar_one_or_none()
            if not dept:
                dept = Department(name=name, code=code)
                db.add(dept)
                await db.flush()
            dept_objs[code] = dept

        # 3. Seed Skills
        logger.info("Seeding default engineering skills...")
        skills = [
            ("C Programming", "Embedded Systems"),
            ("MATLAB Simulink", "Control Systems"),
            ("CAN Bus Diagnostics", "Automotive Communication"),
            ("ECU Flash Programming", "Automotive Communication"),
            ("PID Control Damping", "Control Systems"),
            ("Python FastAPI", "Backend Development"),
            ("PostgreSQL Administration", "Databases"),
            ("Docker Orchestration", "DevOps")
        ]
        skill_objs = {}
        for name, cat in skills:
            res = await db.execute(select(Skill).where(Skill.name == name))
            skill = res.scalar_one_or_none()
            if not skill:
                skill = Skill(name=name, category=cat)
                db.add(skill)
                await db.flush()
            skill_objs[name] = skill

        # 4. Seed Simulation Models
        logger.info("Seeding default simulation models...")
        sims = [
            ("PID Control", "pid_model.slx", "Closed-loop feedback damping and overshoot control loop models."),
            ("CAN Bus", "can_model.slx", "Automotive communication packet scheduler and frame collision simulator."),
            ("ECU Engine", "ecu_model.slx", "Electronic Control Unit throttle angle speed actuator logging simulator.")
        ]
        for name, file, desc in sims:
            res = await db.execute(select(Simulation).where(Simulation.name == name))
            sim = res.scalar_one_or_none()
            if not sim:
                sim = Simulation(name=name, model_file=file, description=desc)
                db.add(sim)
                await db.flush()

        # 5. Seed Default Users & Profiles
        logger.info("Seeding test accounts...")
        users_to_seed = [
            ("admin@bosch.com", "admin123", "Admin", "Alice", "Director", "IT"),
            ("manager@bosch.com", "manager123", "Manager", "Marcus", "Team Lead", "EPS"),
            ("employee@bosch.com", "employee123", "Employee", "Edward", "Engineer", "EPS")
        ]
        
        for email, password, role_name, fname, lname, dept_code in users_to_seed:
            res = await db.execute(select(User).where(User.email == email))
            user = res.scalar_one_or_none()
            if not user:
                hashed = security_service.hash_password(password)
                user = User(
                    email=email,
                    password_hash=hashed,
                    role_id=role_objs[role_name].id,
                    is_active=True
                )
                db.add(user)
                await db.flush()
                
                # Create Profile
                profile = UserProfile(
                    user_id=user.id,
                    first_name=fname,
                    last_name=lname,
                    experience_years=4,
                    department_id=dept_objs[dept_code].id,
                    learning_history={"completed_quizzes": [], "completed_simulations": []}
                )
                db.add(profile)
                await db.flush()
                
                # Add default skills to Employee user
                if role_name == "Employee":
                    # Add MATLAB and C programming to Employee
                    ps1 = ProfileSkill(profile_id=profile.id, skill_id=skill_objs["MATLAB Simulink"].id, level=2)
                    ps2 = ProfileSkill(profile_id=profile.id, skill_id=skill_objs["C Programming"].id, level=3)
                    db.add(ps1)
                    db.add(ps2)
                    await db.flush()

        await db.commit()
        logger.info("Database initialized and seeded successfully.")
        
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(init_db())
