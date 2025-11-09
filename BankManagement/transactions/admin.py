"""
Transaction Admin Configuration - Customizes Django admin interface for Transaction model

This file configures how the Transaction model appears and behaves
in the Django admin panel.
"""

from django.contrib import admin
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """
    Admin configuration for Transaction model
    
    This class customizes:
    - Which fields are displayed in the list view
    - Which fields can be filtered
    - Which fields can be searched
    - How the form is organized
    - Date-based navigation
    """
    
    # ========== LIST VIEW CONFIGURATION ==========
    # Fields to display in the admin list view (table of all transactions)
    list_display = [
        'id',                        # Transaction ID
        'transaction_type',          # Type (Deposit, Withdrawal, Transfer)
        'amount',                    # Transaction amount
        'from_account',              # Source account (if applicable)
        'to_account',                # Destination account (if applicable)
        'status',                     # Transaction status
        'balance_after_transaction',  # Account balance after transaction
        'created_at'                  # When transaction occurred
    ]
    
    # ========== FILTERING CONFIGURATION ==========
    # Fields that can be used to filter transactions
    list_filter = [
        'transaction_type',  # Filter by Deposit, Withdrawal, Transfer, Interest
        'status',            # Filter by Pending, Completed, Failed
        'created_at'         # Filter by date
    ]
    
    # ========== SEARCH CONFIGURATION ==========
    # Fields that can be searched
    # Note: Using __ to search related fields (account numbers)
    search_fields = [
        'from_account__account_number',  # Search by source account number
        'to_account__account_number',    # Search by destination account number
        'description'                     # Search in transaction description
    ]
    
    # ========== READ-ONLY FIELDS ==========
    # Fields that cannot be edited (auto-generated)
    readonly_fields = [
        'created_at'  # Set automatically when transaction is created
    ]
    
    # ========== DATE HIERARCHY ==========
    # Adds date navigation links at the top of the admin list
    # Allows filtering by year, month, and day
    date_hierarchy = 'created_at'
    
    # ========== FORM ORGANIZATION ==========
    # Organize form fields into logical sections
    fieldsets = (
        # Section 1: Transaction Details
        ('Transaction Details', {
            'fields': ('transaction_type', 'amount', 'description', 'status')
        }),
        # Section 2: Accounts Involved
        ('Accounts', {
            'fields': ('from_account', 'to_account')
        }),
        # Section 3: Balance Information
        ('Balance', {
            'fields': ('balance_after_transaction',)
        }),
        # Section 4: Timestamp
        ('Timestamp', {
            'fields': ('created_at',)  # Read-only timestamp
        }),
    )
