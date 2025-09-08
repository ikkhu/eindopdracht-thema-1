from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
import logging

app = Flask(__name__)
CORS(app)

# Database configuratie
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://taskuser:taskpass@db:5432/taskdb')
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Logging configuratie
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database model
class Task(db.Model):
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description
        }

# Maak tabellen aan bij opstart
def create_tables():
    try:
        db.create_all()
        logger.info("Database tabellen aangemaakt")
    except Exception as e:
        logger.error(f"Fout bij aanmaken tabellen: {e}")

# Routes
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/admin')
def admin():
    return send_from_directory('.', 'admin.html')

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Haal alle taken op"""
    try:
        tasks = Task.query.order_by(Task.id.desc()).all()
        return jsonify([task.to_dict() for task in tasks])
    except Exception as e:
        logger.error(f"Fout bij ophalen taken: {e}")
        return jsonify({'error': 'Kon taken niet ophalen'}), 500

@app.route('/api/tasks', methods=['POST'])
def add_task():
    """Voeg nieuwe taak toe"""
    try:
        data = request.get_json()
        
        if not data or 'title' not in data or 'description' not in data:
            return jsonify({'error': 'Titel en beschrijving zijn verplicht'}), 400
        
        if not data['title'].strip() or not data['description'].strip():
            return jsonify({'error': 'Titel en beschrijving mogen niet leeg zijn'}), 400
        
        new_task = Task(
            title=data['title'].strip(),
            description=data['description'].strip()
        )
        
        db.session.add(new_task)
        db.session.commit()
        
        logger.info(f"Nieuwe taak toegevoegd: {new_task.title}")
        return jsonify(new_task.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Fout bij toevoegen taak: {e}")
        return jsonify({'error': 'Kon taak niet toevoegen'}), 500

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Verwijder taak"""
    try:
        task = Task.query.get_or_404(task_id)
        
        db.session.delete(task)
        db.session.commit()
        
        logger.info(f"Taak verwijderd: {task.title}")
        return jsonify({'message': 'Taak succesvol verwijderd'})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Fout bij verwijderen taak: {e}")
        return jsonify({'error': 'Kon taak niet verwijderen'}), 500

# Health check endpoint
@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Taakbeheer API draait'}), 200

if __name__ == '__main__':
    # Wacht even voordat we tabellen aanmaken (database moet opstarten)
    import time
    time.sleep(5)
    
    with app.app_context():
        create_tables()
    
    app.run(host='0.0.0.0', port=5000, debug=False)