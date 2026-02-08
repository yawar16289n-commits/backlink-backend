from flask import Blueprint, request, jsonify
from database import db
from models import Backlink, Website
from utils import extract_domain, validate_da_spam_score
from sqlalchemy import or_

bp = Blueprint('backlinks', __name__, url_prefix='/backlinks')

@bp.route('', methods=['GET'])
def get_backlinks():
    """Get all backlinks with optional filters"""
    try:
        query = Backlink.query
        
        # Search filter
        search = request.args.get('search', '').strip()
        if search:
            query = query.join(Website).filter(
                or_(
                    Backlink.backlink_url.contains(search),
                    Backlink.backlink_website.contains(search),
                    Backlink.da.like(f'%{search}%'),
                    Backlink.spam_score.like(f'%{search}%'),
                    Backlink.id.like(f'%{search}%'),
                    Website.name.contains(search)
                )
            )
        
        # Website filter and "websites without backlinks" filter
        website_id = request.args.get('website_id')
        no_backlinks = request.args.get('no_backlinks')
        
        if no_backlinks == 'true' and website_id:
            # Show backlink records from OTHER websites that the selected website doesn't have
            # Get all backlink_website domains that the selected website DOES have
            existing_backlink_websites = db.session.query(Backlink.backlink_website).filter(
                Backlink.website_id == website_id
            ).distinct().all()
            existing_domains = [b[0] for b in existing_backlink_websites]
            
            # Get backlink records from OTHER websites where backlink_website is NOT in existing_domains
            # Group by backlink_website to show only one record per unique domain
            subquery = db.session.query(
                Backlink.backlink_website,
                db.func.min(Backlink.id).label('min_id')
            ).filter(
                Backlink.website_id != website_id,
                ~Backlink.backlink_website.in_(existing_domains) if existing_domains else True
            ).group_by(Backlink.backlink_website).subquery()
            
            backlinks = Backlink.query.join(
                subquery,
                Backlink.id == subquery.c.min_id
            ).order_by(Backlink.backlink_website).all()
            
            return jsonify([backlink.to_dict() for backlink in backlinks]), 200
        
        elif website_id:
            query = query.filter(Backlink.website_id == website_id)
        
        backlinks = query.order_by(Backlink.created_at.desc()).all()
        return jsonify([backlink.to_dict() for backlink in backlinks]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:id>', methods=['GET'])
def get_backlink(id):
    """Get a single backlink by ID"""
    try:
        backlink = Backlink.query.get(id)
        if not backlink:
            return jsonify({'error': 'Backlink not found'}), 404
        
        return jsonify(backlink.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('', methods=['POST'])
def create_backlink():
    """Create a new backlink"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({'error': 'Request data is required'}), 400
        
        required_fields = ['website_id', 'backlink_url', 'da', 'spam_score']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate website exists
        website = Website.query.get(data['website_id'])
        if not website:
            return jsonify({'error': 'Website not found'}), 404
        
        # Validate backlink URL
        backlink_url = data['backlink_url'].strip()
        if not backlink_url:
            return jsonify({'error': 'Backlink URL cannot be empty'}), 400
        
        # Extract domain from backlink URL
        backlink_website = extract_domain(backlink_url)
        if not backlink_website:
            return jsonify({'error': 'Could not extract domain from URL'}), 400
        
        # Validate DA
        is_valid, result = validate_da_spam_score(data['da'])
        if not is_valid:
            return jsonify({'error': f'DA: {result}'}), 400
        da = result
        
        # Validate Spam Score
        is_valid, result = validate_da_spam_score(data['spam_score'])
        if not is_valid:
            return jsonify({'error': f'Spam Score: {result}'}), 400
        spam_score = result
        
        # Create backlink
        backlink = Backlink(
            website_id=data['website_id'],
            backlink_url=backlink_url,
            backlink_website=backlink_website,
            da=da,
            spam_score=spam_score
        )
        
        db.session.add(backlink)
        db.session.commit()
        
        return jsonify(backlink.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:id>', methods=['PUT'])
def update_backlink(id):
    """Update a backlink"""
    try:
        backlink = Backlink.query.get(id)
        if not backlink:
            return jsonify({'error': 'Backlink not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request data is required'}), 400
        
        # Update website_id if provided
        if 'website_id' in data:
            website = Website.query.get(data['website_id'])
            if not website:
                return jsonify({'error': 'Website not found'}), 404
            backlink.website_id = data['website_id']
        
        # Update backlink URL and extract domain if provided
        if 'backlink_url' in data:
            backlink_url = data['backlink_url'].strip()
            if not backlink_url:
                return jsonify({'error': 'Backlink URL cannot be empty'}), 400
            
            backlink_website = extract_domain(backlink_url)
            if not backlink_website:
                return jsonify({'error': 'Could not extract domain from URL'}), 400
            
            backlink.backlink_url = backlink_url
            backlink.backlink_website = backlink_website
        
        # Update DA if provided
        if 'da' in data:
            is_valid, result = validate_da_spam_score(data['da'])
            if not is_valid:
                return jsonify({'error': f'DA: {result}'}), 400
            backlink.da = result
        
        # Update Spam Score if provided
        if 'spam_score' in data:
            is_valid, result = validate_da_spam_score(data['spam_score'])
            if not is_valid:
                return jsonify({'error': f'Spam Score: {result}'}), 400
            backlink.spam_score = result
        
        db.session.commit()
        
        return jsonify(backlink.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:id>', methods=['DELETE'])
def delete_backlink(id):
    """Delete a backlink"""
    try:
        backlink = Backlink.query.get(id)
        if not backlink:
            return jsonify({'error': 'Backlink not found'}), 404
        
        db.session.delete(backlink)
        db.session.commit()
        
        return jsonify({'message': 'Backlink deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
