"""
Account URL Configuration - Defines URL patterns for account-related views

This file maps URLs to view functions for the accounts app.
URL patterns are matched in order, so more specific patterns should come first.
"""

from django.urls import path
from . import views

# App name: Used for namespacing URLs
# Allows using 'accounts:home' instead of just 'home' to avoid conflicts
app_name = 'accounts'

# URL patterns: List of URL-to-view mappings
urlpatterns = [
    # Home page (dashboard): Empty string means root URL for this app
    # Example: http://127.0.0.1:8000/
    path('', views.home, name='home'),
    
    # Create account page
    # Example: http://127.0.0.1:8000/create/
    path('create/', views.account_create, name='account_create'),
    
    # List all accounts page (requires login)
    # Example: http://127.0.0.1:8000/list/
    path('list/', views.account_list, name='account_list'),
    
    # Account login page (default landing page)
    # Example: http://127.0.0.1:8000/login/
    path('login/', views.account_login, name='account_login'),
    
    # Logout page
    # Example: http://127.0.0.1:8000/logout/
    path('logout/', views.account_logout, name='account_logout'),
    
    # Account detail page: Shows logged-in user's account details
    # Example: http://127.0.0.1:8000/account/
    path('account/', views.account_detail, name='account_detail'),
]
