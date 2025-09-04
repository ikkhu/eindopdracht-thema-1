from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///items.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)

def serialize_item(item: Item) -> dict:
    return {"id": item.id, "name": item.name}

with app.app_context():
    db.create_all()

@app.errorhandler(400)
def bad_request(e):
    return jsonify({"error": "bad_request", "message": str(e)}), 400

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "not_found", "message": str(e)}), 404

@app.route("/items", methods=["POST"])
def create_item():
    data = request.get_json(silent=True)
    if not data or "name" not in data:
        abort(400, description="JSON body with 'name' is required")
    item = Item(name=data["name"].strip())
    try:
        db.session.add(item)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        abort(400, description="Item with that name already exists")
    return jsonify(serialize_item(item)), 201

@app.route("/items", methods=["GET"])
def list_items():
    items = Item.query.order_by(Item.id.asc()).all()
    return jsonify([serialize_item(i) for i in items]), 200

@app.route("/items/<int:item_id>", methods=["PUT"])
def update_item(item_id):
    item = Item.query.get_or_404(item_id)
    data = request.get_json(silent=True)
    if not data or "name" not in data:
        abort(400, description="JSON body with 'name' is required")
    item.name = data["name"].strip()
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        abort(400, description="Item with that name already exists")
    return jsonify(serialize_item(item)), 200

@app.route("/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "Item deleted"}), 200

if __name__ == "__main__":
    app.run(debug=True)
