from app import db
from datetime import datetime
import json


class ExpenseGroup(db.Model):
    """Represents a group of expenses for settlement calculation"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, default="Expense Group")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    expenses = db.relationship('Expense', backref='group', lazy=True, cascade='all, delete-orphan')
    people = db.relationship('Person', backref='group', lazy=True, cascade='all, delete-orphan')

class Person(db.Model):
    """Represents a person in an expense group"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('expense_group.id'), nullable=False)
    
    # Relationships
    paid_expenses = db.relationship('Expense', backref='payer', lazy=True)

class Expense(db.Model):
    """Represents an individual expense"""
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payer_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('expense_group.id'), nullable=False)
    participants_json = db.Column(db.Text, nullable=False)  # JSON list of participant IDs
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def participants(self):
        """Get list of participant IDs"""
        return json.loads(self.participants_json) if self.participants_json else []
    
    @participants.setter
    def participants(self, participant_list):
        """Set list of participant IDs"""
        self.participants_json = json.dumps(participant_list)
    
    @property
    def amount_per_person(self):
        """Calculate amount each participant owes"""
        participant_count = len(self.participants)
        return self.amount / participant_count if participant_count > 0 else 0
