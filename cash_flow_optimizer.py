import heapq
from collections import defaultdict
import logging

class CashFlowOptimizer:
    """
    Optimizes cash flow using graph theory and min-heap algorithms
    to minimize the number of transactions needed to settle debts.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def calculate_net_balances(self, expenses, people):
        """
        Calculate net balance for each person based on expenses.
        
        Args:
            expenses: List of expense objects
            people: List of person objects
            
        Returns:
            dict: {person_id: net_balance} where positive means owed money, negative means owes money
        """
        balances = defaultdict(float)
        
        # Initialize all people with 0 balance
        for person in people:
            balances[person.id] = 0.0
        
        # Process each expense
        for expense in expenses:
            amount_per_person = expense.amount_per_person
            
            # Payer gets credited for the full amount
            balances[expense.payer_id] += expense.amount
            
            # Each participant (including payer) gets debited their share
            for participant_id in expense.participants:
                balances[participant_id] -= amount_per_person
        
        # Round to 2 decimal places to avoid floating point precision issues
        for person_id in balances:
            balances[person_id] = round(balances[person_id], 2)
        
        self.logger.debug(f"Calculated net balances: {dict(balances)}")
        return dict(balances)
    
    def optimize_transactions(self, net_balances, people_dict):
        """
        Use min-heap algorithm to minimize number of transactions.
        
        Args:
            net_balances: dict of {person_id: net_balance}
            people_dict: dict of {person_id: person_name}
            
        Returns:
            list: List of transaction dictionaries with keys: from_person, to_person, amount
        """
        transactions = []
        
        # Separate debtors (negative balance) and creditors (positive balance)
        debtors = []  # min-heap (most negative first)
        creditors = []  # max-heap (most positive first, so we negate values)
        
        for person_id, balance in net_balances.items():
            if balance < -0.01:  # Small threshold to handle floating point precision
                heapq.heappush(debtors, (balance, person_id))  # balance is negative
            elif balance > 0.01:
                heapq.heappush(creditors, (-balance, person_id))  # negate for max-heap behavior
        
        self.logger.debug(f"Debtors heap: {debtors}")
        self.logger.debug(f"Creditors heap: {creditors}")
        
        # Process transactions
        step = 1
        while debtors and creditors:
            # Get the person who owes the most and the person who is owed the most
            debt_amount, debtor_id = heapq.heappop(debtors)
            credit_amount, creditor_id = heapq.heappop(creditors)
            
            debt_amount = abs(debt_amount)  # Convert to positive
            credit_amount = abs(credit_amount)  # Convert to positive
            
            # Calculate transaction amount (minimum of debt and credit)
            transaction_amount = min(debt_amount, credit_amount)
            transaction_amount = round(transaction_amount, 2)
            
            # Record the transaction
            transaction = {
                'step': step,
                'from_person': people_dict[debtor_id],
                'from_person_id': debtor_id,
                'to_person': people_dict[creditor_id],
                'to_person_id': creditor_id,
                'amount': transaction_amount
            }
            transactions.append(transaction)
            
            self.logger.debug(f"Transaction {step}: {people_dict[debtor_id]} pays {people_dict[creditor_id]} ₹{transaction_amount}")
            
            # Update remaining balances
            remaining_debt = debt_amount - transaction_amount
            remaining_credit = credit_amount - transaction_amount
            
            # If debtor still owes money, put them back in the heap
            if remaining_debt > 0.01:
                heapq.heappush(debtors, (-remaining_debt, debtor_id))
            
            # If creditor is still owed money, put them back in the heap
            if remaining_credit > 0.01:
                heapq.heappush(creditors, (-remaining_credit, creditor_id))
            
            step += 1
        
        self.logger.info(f"Optimized to {len(transactions)} transactions")
        return transactions
    
    def get_optimization_summary(self, net_balances, transactions, people_dict):
        """
        Generate a summary of the optimization process.
        
        Returns:
            dict: Summary information including statistics and analysis
        """
        total_debt = sum(abs(balance) for balance in net_balances.values() if balance < 0)
        total_credit = sum(balance for balance in net_balances.values() if balance > 0)
        
        # Count how many direct transactions would be needed without optimization
        debtors_count = sum(1 for balance in net_balances.values() if balance < 0)
        creditors_count = sum(1 for balance in net_balances.values() if balance > 0)
        
        # In worst case, each debtor would pay each creditor
        max_possible_transactions = debtors_count * creditors_count
        
        summary = {
            'total_amount_involved': round(total_debt, 2),
            'optimized_transactions': len(transactions),
            'max_possible_transactions': max_possible_transactions,
            'savings': max_possible_transactions - len(transactions),
            'efficiency_percentage': round(((max_possible_transactions - len(transactions)) / max_possible_transactions * 100), 1) if max_possible_transactions > 0 else 0,
            'people_with_debt': debtors_count,
            'people_with_credit': creditors_count
        }
        
        return summary
