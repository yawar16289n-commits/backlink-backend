from flask import Blueprint, request, jsonify
from database import db
from models import Website, Backlink

bp = Blueprint('websites', __name__, url_prefix='/websites')

@bp.route('', methods=['GET'])
def get_websites():
    """Get all websites"""
    try:
        websites = Website.query.order_by(Website.created_at.desc()).all()
        return jsonify([website.to_dict() for website in websites]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('', methods=['POST'])
def create_website():
    """Create a new website"""
    try:
        data = request.get_json()
        
        if not data or 'name' not in data:
            return jsonify({'error': 'Website name is required'}), 400
        
        name = data['name'].strip()
        if not name:
            return jsonify({'error': 'Website name cannot be empty'}), 400
        
        website = Website(name=name)
        db.session.add(website)
        db.session.commit()
        
        return jsonify(website.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:id>', methods=['PUT'])
def update_website(id):
    """Update a website"""
    try:
        website = Website.query.get(id)
        if not website:
            return jsonify({'error': 'Website not found'}), 404
        
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({'error': 'Website name is required'}), 400
        
        name = data['name'].strip()
        if not name:
            return jsonify({'error': 'Website name cannot be empty'}), 400
        
        website.name = name
        db.session.commit()
        
        return jsonify(website.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:id>', methods=['DELETE'])
def delete_website(id):
    """Delete a website and all its backlinks"""
    try:
        website = Website.query.get(id)
        if not website:
            return jsonify({'error': 'Website not found'}), 404
        
        # Delete all backlinks associated with this website first
        Backlink.query.filter_by(website_id=id).delete()
        
        # Then delete the website
        db.session.delete(website)
        db.session.commit()
        
        return jsonify({'message': 'Website deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
