"""
Transaction URL Configuration - Defines URL patterns for transaction-related views

This file maps URLs to view functions for the transactions app.
All URLs are prefixed with 'transactions/' in the main urls.py file.
"""

from django.urls import path
from . import views

# App name: Used for namespacing URLs
# Allows using 'transactions:deposit' instead of just 'deposit'
app_name = 'transactions'

# URL patterns: List of URL-to-view mappings
urlpatterns = [
    # Deposit money page (requires login)
    # Example: http://127.0.0.1:8000/transactions/deposit/
    path('deposit/', views.deposit, name='deposit'),
    
    # Withdraw money page (requires login)
    # Example: http://127.0.0.1:8000/transactions/withdraw/
    path('withdraw/', views.withdraw, name='withdraw'),
    
    # Transfer money page (requires login)
    # Example: http://127.0.0.1:8000/transactions/transfer/
    path('transfer/', views.transfer, name='transfer'),
    
    # Transaction history for logged-in account
    # Example: http://127.0.0.1:8000/transactions/history/
    path('history/', views.transaction_history, name='transaction_history'),
    
    # View all transactions for logged-in account
    # Example: http://127.0.0.1:8000/transactions/all/
    path('all/', views.all_transactions, name='all_transactions'),
]
