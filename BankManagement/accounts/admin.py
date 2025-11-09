"""
Account Admin Configuration - Customizes Django admin interface for Account model

This file configures how the Account model appears and behaves
in the Django admin panel.
"""

from django.contrib import admin
from .models import Account


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    """
    Admin configuration for Account model
    
    This class customizes:
    - Which fields are displayed in the list view
    - Which fields can be filtered
    - Which fields can be searched
    - How the form is organized
    """
    
    # ========== LIST VIEW CONFIGURATION ==========
    # Fields to display in the admin list view (table of all accounts)
    list_display = [
        'account_number',      # Account number
        'get_full_name',       # Custom method to show full name
        'account_type',        # Type of account
        'balance',             # Current balance
        'status',              # Account status
        'email',               # Customer email
        'phone',               # Customer phone
        'created_at'           # When account was created
    ]
    
    # ========== FILTERING CONFIGURATION ==========
    # Fields that can be used to filter accounts in admin panel
    # These appear as filter options on the right side
    list_filter = [
        'account_type',   # Filter by Savings, Current, etc.
        'status',         # Filter by Active, Inactive, Closed
        'created_at'      # Filter by creation date
    ]
    
    # ========== SEARCH CONFIGURATION ==========
    # Fields that can be searched in the admin panel
    # Search box appears at the top of the list view
    search_fields = [
        'account_number',  # Search by account number
        'first_name',      # Search by first name
        'last_name',       # Search by last name
        'email',           # Search by email
        'phone'            # Search by phone number
    ]
    
    # ========== READ-ONLY FIELDS ==========
    # Fields that cannot be edited in admin panel
    # These are auto-generated or system-managed
    readonly_fields = [
        'account_number',  # Auto-generated, shouldn't be changed
        'created_at',      # Set automatically when created
        'updated_at'       # Updated automatically on save
    ]
    
    # ========== FORM ORGANIZATION ==========
    # Organize form fields into logical sections (fieldsets)
    # This makes the admin form easier to use
    fieldsets = (
        # Section 1: Account Information
        ('Account Information', {
            'fields': ('account_number', 'account_type', 'balance', 'status')
        }),
        # Section 2: Customer Information
        ('Customer Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'address', 'date_of_birth')
        }),
        # Section 3: Security
        ('Security', {
            'fields': ('pin',)  # PIN field in its own section
        }),
        # Section 4: Timestamps
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')  # Read-only timestamp fields
        }),
    )
    
    # ========== CUSTOM METHODS ==========
    def get_full_name(self, obj):
        """
        Custom method to display full name in admin list
        
        This method is called for the 'get_full_name' field in list_display.
        It uses the account's get_full_name() method.
        
        Args:
            obj: The Account instance being displayed
            
        Returns:
            Full name string (e.g., "John Doe")
        """
        return obj.get_full_name()
    
    # Set the column header name in admin list
    get_full_name.short_description = 'Full Name'
