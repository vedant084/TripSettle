from flask import render_template, request, redirect, url_for, flash, jsonify
from app import app, db
from models import ExpenseGroup, Person, Expense
from cash_flow_optimizer import CashFlowOptimizer
import json

@app.route('/')
def index():
    """Main page - show existing groups or create new one"""
    groups = ExpenseGroup.query.order_by(ExpenseGroup.created_at.desc()).all()
    return render_template('index.html', groups=groups)

@app.route('/group/<int:group_id>')
def view_group(group_id):
    """View a specific expense group"""
    group = ExpenseGroup.query.get_or_404(group_id)
    people = Person.query.filter_by(group_id=group_id).all()
    expenses = Expense.query.filter_by(group_id=group_id).order_by(Expense.created_at.desc()).all()
    
    return render_template('index.html', 
                         group=group, 
                         people=people, 
                         expenses=expenses,
                         selected_group_id=group_id)

@app.route('/create_group', methods=['POST'])
def create_group():
    """Create a new expense group"""
    group_name = request.form.get('group_name', 'New Expense Group').strip()
    
    if not group_name:
        flash('Group name is required', 'error')
        return redirect(url_for('index'))
    
    group = ExpenseGroup(name=group_name)
    db.session.add(group)
    db.session.commit()
    
    flash(f'Created group: {group_name}', 'success')
    return redirect(url_for('view_group', group_id=group.id))

@app.route('/add_person/<int:group_id>', methods=['POST'])
def add_person(group_id):
    """Add a person to an expense group"""
    group = ExpenseGroup.query.get_or_404(group_id)
    person_name = request.form.get('person_name', '').strip()
    
    if not person_name:
        flash('Person name is required', 'error')
        return redirect(url_for('view_group', group_id=group_id))
    
    # Check if person already exists in this group
    existing_person = Person.query.filter_by(group_id=group_id, name=person_name).first()
    if existing_person:
        flash(f'{person_name} is already in this group', 'error')
        return redirect(url_for('view_group', group_id=group_id))
    
    person = Person(name=person_name, group_id=group_id)
    db.session.add(person)
    db.session.commit()
    
    flash(f'Added {person_name} to the group', 'success')
    return redirect(url_for('view_group', group_id=group_id))

@app.route('/add_expense/<int:group_id>', methods=['POST'])
def add_expense(group_id):
    """Add an expense to a group"""
    group = ExpenseGroup.query.get_or_404(group_id)
    
    description = request.form.get('description', '').strip()
    amount_str = request.form.get('amount', '').strip()
    payer_id = request.form.get('payer_id')
    participant_ids = request.form.getlist('participants')
    
    # Validation
    if not description:
        flash('Expense description is required', 'error')
        return redirect(url_for('view_group', group_id=group_id))
    
    try:
        amount = float(amount_str)
        if amount <= 0:
            raise ValueError("Amount must be positive")
    except (ValueError, TypeError):
        flash('Please enter a valid positive amount', 'error')
        return redirect(url_for('view_group', group_id=group_id))
    
    if not payer_id:
        flash('Please select who paid for this expense', 'error')
        return redirect(url_for('view_group', group_id=group_id))
    
    if not participant_ids:
        flash('Please select at least one participant', 'error')
        return redirect(url_for('view_group', group_id=group_id))
    
    # Verify payer exists in group
    payer = Person.query.filter_by(id=payer_id, group_id=group_id).first()
    if not payer:
        flash('Invalid payer selected', 'error')
        return redirect(url_for('view_group', group_id=group_id))
    
    # Verify all participants exist in group
    participant_ids = [int(pid) for pid in participant_ids]
    participants_in_group = Person.query.filter(
        Person.id.in_(participant_ids), 
        Person.group_id == group_id
    ).count()
    
    if participants_in_group != len(participant_ids):
        flash('Invalid participants selected', 'error')
        return redirect(url_for('view_group', group_id=group_id))
    
    # Create expense
    expense = Expense(
        description=description,
        amount=amount,
        payer_id=payer_id,
        group_id=group_id,
        participants=participant_ids
    )
    
    db.session.add(expense)
    db.session.commit()
    
    flash(f'Added expense: {description} (₹{amount})', 'success')
    return redirect(url_for('view_group', group_id=group_id))

@app.route('/calculate_settlement/<int:group_id>')
def calculate_settlement(group_id):
    """Calculate optimized settlement for a group"""
    group = ExpenseGroup.query.get_or_404(group_id)
    people = Person.query.filter_by(group_id=group_id).all()
    expenses = Expense.query.filter_by(group_id=group_id).all()
    
    if not people:
        flash('Add some people to the group first', 'error')
        return redirect(url_for('view_group', group_id=group_id))
    
    if not expenses:
        flash('Add some expenses to calculate settlement', 'error')
        return redirect(url_for('view_group', group_id=group_id))
    
    # Create optimizer and calculate
    optimizer = CashFlowOptimizer()
    
    # Calculate net balances
    net_balances = optimizer.calculate_net_balances(expenses, people)
    
    # Create people dictionary for optimization
    people_dict = {person.id: person.name for person in people}
    
    # Optimize transactions
    transactions = optimizer.optimize_transactions(net_balances, people_dict)
    
    # Get summary
    summary = optimizer.get_optimization_summary(net_balances, transactions, people_dict)
    
    # Prepare balance data for display
    balance_data = []
    for person in people:
        balance = net_balances.get(person.id, 0)
        balance_data.append({
            'name': person.name,
            'balance': balance,
            'status': 'owes' if balance < -0.01 else 'owed' if balance > 0.01 else 'settled'
        })
    
    return render_template('results.html',
                         group=group,
                         balance_data=balance_data,
                         transactions=transactions,
                         summary=summary,
                         people=people,
                         expenses=expenses)

@app.route('/delete_expense/<int:expense_id>')
def delete_expense(expense_id):
    """Delete an expense"""
    expense = Expense.query.get_or_404(expense_id)
    group_id = expense.group_id
    
    db.session.delete(expense)
    db.session.commit()
    
    flash('Expense deleted successfully', 'success')
    return redirect(url_for('view_group', group_id=group_id))

@app.route('/delete_person/<int:person_id>')
def delete_person(person_id):
    """Delete a person from a group"""
    person = Person.query.get_or_404(person_id)
    group_id = person.group_id
    
    # Check if person has any expenses
    expenses_count = Expense.query.filter_by(payer_id=person_id).count()
    if expenses_count > 0:
        flash(f'Cannot delete {person.name} - they have expenses recorded', 'error')
        return redirect(url_for('view_group', group_id=group_id))
    
    # Check if person is a participant in any expenses
    all_expenses = Expense.query.filter_by(group_id=group_id).all()
    for expense in all_expenses:
        if person_id in expense.participants:
            flash(f'Cannot delete {person.name} - they are a participant in expenses', 'error')
            return redirect(url_for('view_group', group_id=group_id))
    
    db.session.delete(person)
    db.session.commit()
    
    flash(f'Removed {person.name} from the group', 'success')
    return redirect(url_for('view_group', group_id=group_id))

@app.route('/export_settlement/<int:group_id>')
def export_settlement(group_id):
    """Export settlement data as JSON"""
    group = ExpenseGroup.query.get_or_404(group_id)
    people = Person.query.filter_by(group_id=group_id).all()
    expenses = Expense.query.filter_by(group_id=group_id).all()
    
    if not expenses:
        flash('No expenses to export', 'error')
        return redirect(url_for('view_group', group_id=group_id))
    
    optimizer = CashFlowOptimizer()
    net_balances = optimizer.calculate_net_balances(expenses, people)
    people_dict = {person.id: person.name for person in people}
    transactions = optimizer.optimize_transactions(net_balances, people_dict)
    summary = optimizer.get_optimization_summary(net_balances, transactions, people_dict)
    
    export_data = {
        'group_name': group.name,
        'export_date': group.created_at.isoformat(),
        'summary': summary,
        'transactions': transactions,
        'balances': {people_dict[pid]: balance for pid, balance in net_balances.items()}
    }
    
    return jsonify(export_data)
