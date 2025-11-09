from django.db import models
from django.core.validators import MinLengthValidator
import random
import string


class Account(models.Model):
    ACCOUNT_TYPE_CHOICES = [
        ('Savings', 'Savings'),
        ('Current', 'Current'),
        ('Fixed Deposit', 'Fixed Deposit'),
        ('Recurring Deposit', 'Recurring Deposit'),
    ]
    
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('Closed', 'Closed'),
    ]
    
    # Account Information
    account_number = models.CharField(max_length=12, unique=True, editable=False)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPE_CHOICES, default='Savings')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')
    
    # Customer Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    date_of_birth = models.DateField()
    
    # Security
    pin = models.CharField(max_length=4, validators=[MinLengthValidator(4)], help_text="4-digit PIN")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Account'
        verbose_name_plural = 'Accounts'
    
    def __str__(self):
        return f"{self.account_number} - {self.first_name} {self.last_name}"
    
    def save(self, *args, **kwargs):
        if not self.account_number:
            self.account_number = self.generate_account_number()
        super().save(*args, **kwargs)
    
    def generate_account_number(self):
        """Generate a unique 12-digit account number"""
        while True:
            account_num = ''.join(random.choices(string.digits, k=12))
            if not Account.objects.filter(account_number=account_num).exists():
                return account_num
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def can_withdraw(self, amount):
        """Check if account can withdraw the specified amount"""
        return self.status == 'Active' and self.balance >= amount
    
    def deposit(self, amount):
        """Deposit money into account"""
        if self.status == 'Active':
            self.balance += amount
            self.save()
            return True
        return False
    
    def withdraw(self, amount):
        """Withdraw money from account"""
        if self.can_withdraw(amount):
            self.balance -= amount
            self.save()
            return True
        return False
