"""Routes package - modular API endpoints"""
from flask import Blueprint

# Create main API blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Import sub-routes
from routes.website_routes import bp as websites_bp
from routes.backlink_routes import bp as backlinks_bp

# Register all sub-blueprints
api_bp.register_blueprint(websites_bp)
api_bp.register_blueprint(backlinks_bp)
