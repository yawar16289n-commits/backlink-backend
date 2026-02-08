from database import db
from datetime import datetime

class Website(db.Model):
    __tablename__ = 'websites'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    backlinks = db.relationship('Backlink', backref='website', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.isoformat()
        }

class Backlink(db.Model):
    __tablename__ = 'backlinks'
    
    id = db.Column(db.Integer, primary_key=True)
    website_id = db.Column(db.Integer, db.ForeignKey('websites.id'), nullable=False)
    backlink_url = db.Column(db.Text, nullable=False)
    backlink_website = db.Column(db.String(255), nullable=False)
    da = db.Column(db.Integer, nullable=False)
    spam_score = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'website_id': self.website_id,
            'website_name': self.website.name if self.website else None,
            'backlink_url': self.backlink_url,
            'backlink_website': self.backlink_website,
            'da': self.da,
            'spam_score': self.spam_score,
            'created_at': self.created_at.isoformat()
        }
