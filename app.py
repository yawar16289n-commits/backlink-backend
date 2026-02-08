from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os
from database import db
from routes import api_bp

load_dotenv()

app = Flask(__name__)
CORS(app)

# Database configuration
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '3306')
DB_NAME = os.getenv('DB_NAME', 'backlink_db')

DATABASE_URL = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Import db from database module
db.init_app(app)

# Import and register routes
app.register_blueprint(api_bp)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
