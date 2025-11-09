"""
Account Decorators - Authentication decorators for account-based access control

This module provides decorators to protect views that require user login.
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from .models import Account


def login_required(view_func):
    """
    Decorator to require account login before accessing a view
    
    This decorator checks if an account is stored in the session.
    If not logged in, redirects to login page.
    
    Usage:
        @login_required
        def my_view(request):
            account = request.session.get('account')
            ...
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Check if account number is stored in session
        account_number = request.session.get('account_number')
        
        if not account_number:
            # Not logged in: redirect to login page
            messages.warning(request, 'Please login to access this page.')
            return redirect('accounts:account_login')
        
        # Check if account still exists and is active
        try:
            account = Account.objects.get(account_number=account_number, status='Active')
            # Store account object in request for easy access
            request.account = account
        except Account.DoesNotExist:
            # Account no longer exists or is inactive: clear session and redirect
            request.session.flush()
            messages.error(request, 'Your account is no longer active. Please contact support.')
            return redirect('accounts:account_login')
        
        # User is logged in: proceed with the view
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view

