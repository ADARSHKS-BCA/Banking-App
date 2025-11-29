"""
Account Model - Defines the structure and behavior of bank accounts

This model represents a bank account with customer information,
account details, and methods for financial operations.
"""

from django.db import models
from django.core.validators import MinLengthValidator
import random
import string


class Account(models.Model):
    """
    Account Model - Represents a bank account in the system
    
    This model stores:
    - Account information (number, type, balance, status)
    - Customer personal information
    - Security credentials (PIN)
    - Timestamps for tracking creation and updates
    """
    
    # Define choices for account types that users can select
    # This  saves the column name has Savings
    ACCOUNT_TYPE_CHOICES = [
        ('Savings', 'Savings'),           # Regular savings account
        ('Current', 'Current'),           # Current/checking account
        ('Fixed Deposit', 'Fixed Deposit'),  # Fixed deposit account
        ('Recurring Deposit', 'Recurring Deposit'),  # Recurring deposit account
    ]
    
    # Define choices for account status
    STATUS_CHOICES = [
        ('Active', 'Active'),      # Account is active and can be used
        ('Inactive', 'Inactive'),  # Account is temporarily inactive
        ('Closed', 'Closed'),      # Account has been closed
    ]
    
    # ========== ACCOUNT INFORMATION FIELDS ==========
    
    # Account number: Auto-generated unique 12-digit number
    # editable=False prevents manual editing in admin panel
    account_number = models.CharField(max_length=12, unique=True, editable=False)
    
    # Account type: Type of bank account (Savings, Current, etc.)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPE_CHOICES, default='Savings')
    
    # Balance: Current account balance (12 digits total, 2 decimal places)
    # Example: 9999999999.99 (max value)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    # Status: Current status of the account (Active, Inactive, Closed)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')
    
    # ========== CUSTOMER INFORMATION FIELDS ==========
    
    # Customer's first name
    first_name = models.CharField(max_length=100)
    
    # Customer's last name
    last_name = models.CharField(max_length=100)
    
    # Email address: Must be unique (one email per account)
    email = models.EmailField(unique=True)
    
    # Phone number: Contact number
    phone = models.CharField(max_length=15)
    
    # Address: Full address of the customer
    address = models.TextField()
    
    # Date of birth: Customer's date of birth
    date_of_birth = models.DateField()
    
    # Profile picture: User's profile photo (optional)
    # Images are uploaded to media/profile_pictures/ directory
    # null=True and blank=True make this field optional
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    
    # ========== SECURITY FIELDS ==========
    
    # PIN: 4-digit personal identification number for account access
    # MinLengthValidator ensures it's exactly 4 characters
    # Note: In production, this should be hashed, not stored in plain text!
    pin = models.CharField(max_length=4, validators=[MinLengthValidator(4)], help_text="4-digit PIN")
    
    # ========== TIMESTAMP FIELDS ==========
    
    # Created timestamp: Automatically set when account is first created
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Updated timestamp: Automatically updated every time the account is saved
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        """
        Meta class: Provides metadata about the model
        
        - ordering: Default ordering for queries (newest first)
        - verbose_name: Human-readable name for single object
        - verbose_name_plural: Human-readable name for multiple objects
        """
        ordering = ['-created_at']  # Order by creation date, newest first
        verbose_name = 'Account'
        verbose_name_plural = 'Accounts'
    
    def __str__(self):
        """
        String representation of the Account object
        
        Returns: A readable string showing account number and customer name
        Example: "123456789012 - John Doe"
        """
        return f"{self.account_number} - {self.first_name} {self.last_name}"
    
    def save(self, *args, **kwargs):
        """
        Override save method to auto-generate account number if it doesn't exist
        
        This method is called automatically when saving an Account instance.
        If the account doesn't have a number yet (new account), it generates one.
        """
        # Only generate account number if it doesn't exist (new account)
        if not self.account_number:
            self.account_number = self.generate_account_number()
        # Call the parent save method to actually save to database
        super().save(*args, **kwargs)
    
    def generate_account_number(self):
        """
        Generate a unique 12-digit account number based on DOB
        
        Format: YYYYMMDD + 4 random digits
        Example: 199001015678
        """
        # Get DOB in YYYYMMDD format
        dob_str = self.date_of_birth.strftime('%Y%m%d')
        
        while True:
            # Generate 4 random digits
            random_digits = ''.join(random.choices(string.digits, k=4))
            # Combine DOB and random digits
            account_num = dob_str + random_digits
            
            # Check if this number already exists
            if not Account.objects.filter(account_number=account_num).exists():
                return account_num
    
    def get_full_name(self):
        """
        Get the full name of the account holder
        
        Returns: First name and last name combined
        Example: "John Doe"
        """
        return f"{self.first_name} {self.last_name}"
    
    def can_withdraw(self, amount):
        """
        Check if the account can withdraw the specified amount
        
        Conditions for withdrawal:
        1. Account must be Active
        2. Balance must be greater than or equal to withdrawal amount
        
        Args:
            amount: The amount to withdraw (Decimal)
            
        Returns:
            True if withdrawal is allowed, False otherwise
        """
        return self.status == 'Active' and self.balance >= amount
    
    def deposit(self, amount):
        """
        Deposit money into the account
        
        This method adds money to the account balance.
        Only works if the account is Active.
        
        Args:
            amount: The amount to deposit (Decimal)
            
        Returns:
            True if deposit successful, False if account is inactive
        """
        # Only allow deposits to active accounts
        if self.status == 'Active':
            # Add amount to balance
            self.balance += amount
            # Save the updated balance to database
            self.save()
            return True
        # Return False if account is not active
        return False
    
    def withdraw(self, amount):
        """
        Withdraw money from the account
        
        This method subtracts money from the account balance.
        Only works if account is Active and has sufficient balance.
        
        Args:
            amount: The amount to withdraw (Decimal)
            
        Returns:
            True if withdrawal successful, False otherwise
        """
        # Check if withdrawal is allowed (uses can_withdraw method)
        if self.can_withdraw(amount):
            # Subtract amount from balance
            self.balance -= amount
            # Save the updated balance to database
            self.save()
            return True
        # Return False if withdrawal not allowed
        return False
