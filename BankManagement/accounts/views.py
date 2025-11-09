"""
Account Views - Handles HTTP requests for account-related pages

These views handle:
- Home page display
- Account creation
- Account listing and searching
- Account detail view
- Account login
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Account
from .forms import AccountForm, AccountLoginForm
from .decorators import login_required


def home(request):
    """
    Home page view - Dashboard for logged-in users
    
    If user is logged in, shows their account dashboard.
    If not logged in, redirects to login page.
    
    Args:
        request: HTTP request object from Django
        
    Returns:
        Rendered HTML template (home.html) or redirect to login
    """
    # Check if user is logged in
    account_number = request.session.get('account_number')
    
    if account_number:
        # User is logged in: show dashboard
        try:
            account = Account.objects.get(account_number=account_number, status='Active')
            # Get recent transactions
            from transactions.models import Transaction
            recent_transactions = Transaction.objects.filter(
                Q(from_account=account) | Q(to_account=account)
            ).order_by('-created_at')[:5]
            
            return render(request, 'accounts/home.html', {
                'account': account,
                'recent_transactions': recent_transactions
            })
        except Account.DoesNotExist:
            # Account doesn't exist: clear session and redirect to login
            request.session.flush()
            return redirect('accounts:account_login')
    else:
        # Not logged in: redirect to login
        return redirect('accounts:account_login')


def account_create(request):
    """
    Create a new bank account view
    
    This view handles both GET and POST requests:
    - GET: Shows the account creation form
    - POST: Processes the form and creates the account, then auto-logs in
    
    Args:
        request: HTTP request object
        
    Returns:
        - If POST and valid: Auto-logs in and redirects to home page
        - Otherwise: Renders account creation form
    """
    # Check if form was submitted (POST request)
    if request.method == 'POST':
        # Create form instance with submitted data and files (for profile picture upload)
        form = AccountForm(request.POST, request.FILES)
        
        # Validate the form
        if form.is_valid():
            # Save the account (this generates account number automatically)
            account = form.save()
            
            # Auto-login: Store account number in session
            request.session['account_number'] = account.account_number
            request.session['account_name'] = account.get_full_name()
            
            # Show success message to user
            messages.success(request, f'Account created successfully! Welcome, {account.get_full_name()}. Your account number is: {account.account_number}')
            
            # Redirect to home page (dashboard)
            return redirect('accounts:home')
    else:
        # GET request: Show empty form
        form = AccountForm()
    
    # Render the form template
    return render(request, 'accounts/account_create.html', {'form': form})


@login_required
def account_list(request):
    """
    List all accounts view with search functionality (Admin/Staff only)
    
    This view displays all accounts in a table format.
    Users can search by account number, name, email, or phone.
    Requires login.
    
    Args:
        request: HTTP request object
        
    Returns:
        Rendered HTML template with list of accounts
    """
    # Get all accounts from database
    accounts = Account.objects.all()
    
    # ========== SEARCH FUNCTIONALITY ==========
    # Get search query from URL parameters (e.g., ?search=john)
    search_query = request.GET.get('search', '')
    
    # If user entered a search query
    if search_query:
        # Filter accounts using Q objects for complex queries
        # Q objects allow OR conditions (| means OR)
        accounts = accounts.filter(
            Q(account_number__icontains=search_query) |  # Search in account number
            Q(first_name__icontains=search_query) |      # Search in first name
            Q(last_name__icontains=search_query) |       # Search in last name
            Q(email__icontains=search_query) |           # Search in email
            Q(phone__icontains=search_query)             # Search in phone
        )
        # icontains means case-insensitive partial match
    
    # Render template with accounts and search query
    return render(request, 'accounts/account_list.html', {
        'accounts': accounts,
        'search_query': search_query  # Pass search query to template to show in input field
    })


@login_required
def account_detail(request):
    """
    View account details and recent transactions
    
    This view shows:
    - All account information
    - Current balance
    - Recent transaction history (last 10)
    
    Users can only view their own account details.
    
    Args:
        request: HTTP request object
        
    Returns:
        Rendered HTML template with account details
    """
    # Get logged-in account
    account = request.account
    
    # ========== GET RECENT TRANSACTIONS ==========
    # Import Transaction model (imported here to avoid circular imports)
    from transactions.models import Transaction
    
    # Get transactions where this account is either sender or receiver
    # Q objects allow OR conditions
    recent_transactions = Transaction.objects.filter(
        Q(from_account=account) |  # Account sent money
        Q(to_account=account)      # Account received money
    ).order_by('-created_at')[:10]  # Order by newest first, limit to 10
    
    # Render template with account and transactions
    return render(request, 'accounts/account_detail.html', {
        'account': account,
        'recent_transactions': recent_transactions
    })


def account_login(request):
    """
    Account login view - Verify account number and PIN
    
    This view handles account authentication:
    - GET: Shows login form (or redirects if already logged in)
    - POST: Validates credentials, stores in session, and redirects to home page
    
    Args:
        request: HTTP request object
        
    Returns:
        - If already logged in: Redirects to home page
        - If valid credentials: Stores in session and redirects to home page
        - Otherwise: Shows login form with error message
    """
    # Check if already logged in
    if request.session.get('account_number'):
        messages.info(request, 'You are already logged in.')
        return redirect('accounts:home')
    
    # Check if form was submitted
    if request.method == 'POST':
        # Create form with submitted data
        form = AccountLoginForm(request.POST)
        
        # Validate form
        if form.is_valid():
            # Get cleaned (validated) data
            account_number = form.cleaned_data['account_number']
            pin = form.cleaned_data['pin']
            
            try:
                # Find account with matching number and active status
                account = Account.objects.get(account_number=account_number, status='Active')
                
                # Verify PIN matches
                if account.pin == pin:
                    # PIN correct: Store account in session
                    request.session['account_number'] = account.account_number
                    request.session['account_name'] = account.get_full_name()
                    
                    # Show success message
                    messages.success(request, f'Welcome back, {account.get_full_name()}!')
                    
                    # Redirect to home page (dashboard)
                    return redirect('accounts:home')
                else:
                    # PIN incorrect: show error message
                    messages.error(request, 'Invalid PIN!')
            except Account.DoesNotExist:
                # Account not found or inactive: show error message
                messages.error(request, 'Account not found or inactive!')
    else:
        # GET request: Show empty login form
        form = AccountLoginForm()
    
    # Render login form template
    return render(request, 'accounts/account_login.html', {'form': form})


def account_logout(request):
    """
    Logout view - Clear session and redirect to login
    
    Args:
        request: HTTP request object
        
    Returns:
        Redirect to login page
    """
    # Clear all session data
    request.session.flush()
    
    # Show logout message
    messages.success(request, 'You have been successfully logged out.')
    
    # Redirect to login page
    return redirect('accounts:account_login')
