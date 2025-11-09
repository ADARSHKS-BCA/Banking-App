from django.db import models
from accounts.models import Account


class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('Deposit', 'Deposit'),
        ('Withdrawal', 'Withdrawal'),
        ('Transfer', 'Transfer'),
        ('Interest', 'Interest'),
    ]
    
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
    ]
    
    # Transaction Details
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Completed')
    
    # Account Relations
    from_account = models.ForeignKey(
        Account, 
        on_delete=models.CASCADE, 
        related_name='transactions_from',
        null=True, 
        blank=True,
        help_text="Account from which money is debited"
    )
    to_account = models.ForeignKey(
        Account, 
        on_delete=models.CASCADE, 
        related_name='transactions_to',
        null=True, 
        blank=True,
        help_text="Account to which money is credited"
    )
    
    # Balance tracking
    balance_after_transaction = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
    
    def __str__(self):
        return f"{self.transaction_type} - {self.amount} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    def get_account_display(self):
        """Get the account involved in transaction"""
        if self.transaction_type == 'Deposit':
            return self.to_account
        elif self.transaction_type == 'Withdrawal':
            return self.from_account
        elif self.transaction_type == 'Transfer':
            return f"{self.from_account.account_number} → {self.to_account.account_number}"
        return None
