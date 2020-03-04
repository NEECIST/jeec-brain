import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID

db = SQLAlchemy()
db.UUID = UUID(as_uuid=True)
db_session = db.session


def create_tables():
    # Event
    from jeec_brain.models.events import Events
    
    from jeec_brain.models.companies import Companies
    from jeec_brain.models.students import Students
    from jeec_brain.models.colaborators import Colaborators
    from jeec_brain.models.speakers import Speakers
    from jeec_brain.models.users import Users
    from jeec_brain.models.teams import Teams

    # Activities
    from jeec_brain.models.activity_types import ActivityTypes
    from jeec_brain.models.activities import Activities
    from jeec_brain.models.company_activities import CompanyActivities
    from jeec_brain.models.speaker_activities import SpeakerActivities

    # Auctions
    from jeec_brain.models.auctions import Auctions
    from jeec_brain.models.company_auctions import CompanyAuctions

    # Resumes
    from jeec_brain.models.resume_submissions import ResumeSubmissions
    from jeec_brain.models.company_resume_submissions import CompanyResumeSubmissions

    # Meals
    from jeec_brain.models.meals import Meals
    from jeec_brain.models.dishes import Dishes
    from jeec_brain.models.company_meals import CompanyMeals
    from jeec_brain.models.company_dishes import CompanyDishes

    # News
    from jeec_brain.models.news import News
    
    db.create_all()


def drop_tables():
    db.reflect()
    db.drop_all()


def create_testing_db():
    conn = db.engine.connect()
    conn.execute('commit')  # stop open transaction
    conn.execute('create database test_' + os.environ['APP_DB'])
    conn.close()