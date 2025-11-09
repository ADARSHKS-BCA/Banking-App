from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Account
from .forms import AccountForm, AccountLoginForm


def home(request):
    """Home page"""
    return render(request, 'accounts/home.html')


def account_create(request):
    """Create a new bank account"""
    if request.method == 'POST':
        form = AccountForm(request.POST)
        if form.is_valid():
            account = form.save()
            messages.success(request, f'Account created successfully! Your account number is: {account.account_number}')
            return redirect('account_detail', account_number=account.account_number)
    else:
        form = AccountForm()
    return render(request, 'accounts/account_create.html', {'form': form})


def account_list(request):
    """List all accounts"""
    accounts = Account.objects.all()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        accounts = accounts.filter(
            Q(account_number__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
    
    return render(request, 'accounts/account_list.html', {
        'accounts': accounts,
        'search_query': search_query
    })


def account_detail(request, account_number):
    """View account details"""
    account = get_object_or_404(Account, account_number=account_number)
    
    # Get recent transactions
    from transactions.models import Transaction
    recent_transactions = Transaction.objects.filter(
        Q(from_account=account) | Q(to_account=account)
    ).order_by('-created_at')[:10]
    
    return render(request, 'accounts/account_detail.html', {
        'account': account,
        'recent_transactions': recent_transactions
    })


def account_login(request):
    """Login to view account"""
    if request.method == 'POST':
        form = AccountLoginForm(request.POST)
        if form.is_valid():
            account_number = form.cleaned_data['account_number']
            pin = form.cleaned_data['pin']
            
            try:
                account = Account.objects.get(account_number=account_number, status='Active')
                if account.pin == pin:
                    return redirect('account_detail', account_number=account.account_number)
                else:
                    messages.error(request, 'Invalid PIN!')
            except Account.DoesNotExist:
                messages.error(request, 'Account not found or inactive!')
    else:
        form = AccountLoginForm()
    
    return render(request, 'accounts/account_login.html', {'form': form})
