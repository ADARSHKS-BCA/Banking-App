"""
Transaction Model - Defines the structure for all financial transactions

This model records all money movements in the bank system including
deposits, withdrawals, transfers, and interest payments.
"""

from django.db import models
from accounts.models import Account


class Transaction(models.Model):
    """
    Transaction Model - Represents a financial transaction in the system
    
    This model stores:
    - Transaction type (Deposit, Withdrawal, Transfer, Interest)
    - Amount involved in the transaction
    - Source and destination accounts
    - Transaction status and description
    - Balance after transaction for audit purposes
    """
    
    # Define choices for transaction types
    TRANSACTION_TYPE_CHOICES = [
        ('Deposit', 'Deposit'),           # Money added to an account
        ('Withdrawal', 'Withdrawal'),     # Money removed from an account
        ('Transfer', 'Transfer'),         # Money moved between accounts
        ('Interest', 'Interest'),         # Interest payment added to account
    ]
    
    # Define choices for transaction status
    STATUS_CHOICES = [
        ('Pending', 'Pending'),      # Transaction is pending processing
        ('Completed', 'Completed'),  # Transaction successfully completed
        ('Failed', 'Failed'),        # Transaction failed
    ]
    
    # ========== TRANSACTION DETAIL FIELDS ==========
    
    # Transaction type: What kind of transaction this is
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    
    # Amount: The monetary value of the transaction
    # 12 digits total, 2 decimal places (max: 9999999999.99)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Description: Optional notes about the transaction
    description = models.TextField(blank=True, null=True)
    
    # Status: Current status of the transaction
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Completed')
    
    # ========== ACCOUNT RELATION FIELDS ==========
    
    # From Account: The account from which money is debited (removed)
    # null=True and blank=True because deposits don't have a "from" account
    # related_name allows accessing transactions from Account: account.transactions_from.all()
    from_account = models.ForeignKey(
        Account,  # Related to Account model
        on_delete=models.CASCADE,  # If account is deleted, delete all its transactions
        related_name='transactions_from',  # Access via: account.transactions_from.all()
        null=True,  # Can be empty (for deposits)
        blank=True,  # Can be empty in forms
        help_text="Account from which money is debited"
    )
    
    # To Account: The account to which money is credited (added)
    # null=True and blank=True because withdrawals don't have a "to" account
    # related_name allows accessing transactions from Account: account.transactions_to.all()
    to_account = models.ForeignKey(
        Account,  # Related to Account model
        on_delete=models.CASCADE,  # If account is deleted, delete all its transactions
        related_name='transactions_to',  # Access via: account.transactions_to.all()
        null=True,  # Can be empty (for withdrawals)
        blank=True,  # Can be empty in forms
        help_text="Account to which money is credited"
    )
    
    # ========== BALANCE TRACKING FIELD ==========
    
    # Balance after transaction: Stores the account balance after this transaction
    # This is useful for audit trails and account statements
    # null=True because it might not be set for pending transactions
    balance_after_transaction = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # ========== TIMESTAMP FIELD ==========
    
    # Created timestamp: When the transaction was created
    # auto_now_add=True means it's set automatically when transaction is created
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        """
        Meta class: Provides metadata about the model
        
        - ordering: Default ordering for queries (newest first)
        - verbose_name: Human-readable name for single object
        - verbose_name_plural: Human-readable name for multiple objects
        """
        ordering = ['-created_at']  # Order by date, newest transactions first
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
    
    def __str__(self):
        """
        String representation of the Transaction object
        
        Returns: A readable string showing type, amount, and date
        Example: "Deposit - 1000.00 - 2024-01-15 10:30"
        """
        return f"{self.transaction_type} - {self.amount} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    def get_account_display(self):
        """
        Get the account(s) involved in this transaction
        
        This method returns different information based on transaction type:
        - Deposit: Returns the account receiving money
        - Withdrawal: Returns the account losing money
        - Transfer: Returns a string showing both account numbers
        
        Returns:
            Account object or string representation, or None
        """
        if self.transaction_type == 'Deposit':
            # Deposits only have a "to_account"
            return self.to_account
        elif self.transaction_type == 'Withdrawal':
            # Withdrawals only have a "from_account"
            return self.from_account
        elif self.transaction_type == 'Transfer':
            # Transfers have both accounts, show arrow between them
            return f"{self.from_account.account_number} → {self.to_account.account_number}"
        return None
