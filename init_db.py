from app import app
from database import db
from models import Website, Backlink

def init_db():
    """Initialize the database - create all tables"""
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database tables created successfully!")

if __name__ == '__main__':
    init_db()
