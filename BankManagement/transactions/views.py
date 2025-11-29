"""
Transaction Views - Handles HTTP requests for transaction operations

These views handle:
- Depositing money
- Withdrawing money
- Transferring money between accounts
- Viewing transaction history
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction  # Note: This is Django's transaction module, not our model!
from .models import Transaction
from accounts.models import Account
from accounts.decorators import login_required
from .forms import DepositForm, WithdrawalForm, TransferForm


@login_required
def deposit(request):
    """
    Deposit money into logged-in account view
    
    This view handles adding money to the logged-in user's account:
    - GET: Shows deposit form (account number pre-filled)
    - POST: Processes deposit and updates account balance
    
    Args:
        request: HTTP request object
        
    Returns:
        - If successful: Redirects to home page
        - Otherwise: Shows deposit form with errors
    """
    # Get logged-in account
    account = request.account
    
    # Check if form was submitted
    if request.method == 'POST':
        # Create form with submitted data
        form = DepositForm(request.POST, account=account)
        
        # Validate form
        if form.is_valid():
            # Get cleaned (validated) data
            amount = form.cleaned_data['amount']
            description = form.cleaned_data.get('description', '')  # Optional field
            
            # ========== PERFORM DEPOSIT ==========
            # Use the account's deposit method to add money
            account.deposit(amount)
            
            # ========== CREATE TRANSACTION RECORD ==========
            # Record the transaction in database for audit trail
            Transaction.objects.create(
                transaction_type='Deposit',  # Type of transaction
                amount=amount,                # Amount deposited
                to_account=account,           # Account receiving money
                description=description if description else 'Deposit',  # Default to 'Deposit'
                balance_after_transaction=account.balance,  # Balance after deposit
                status='Completed'           # Transaction completed successfully
            )
            
            # Show success message
            messages.success(request, f'Successfully deposited ${amount} to your account. New balance: ${account.balance}')
            
            # Redirect to home page
            return redirect('accounts:home')
    else:
        # GET request: Show deposit form with account pre-filled
        form = DepositForm(account=account)
    
    # Render deposit form template
    return render(request, 'transactions/deposit.html', {'form': form, 'account': account})


@login_required
def withdraw(request):
    """
    Withdraw money from logged-in account view
    
    This view handles removing money from the logged-in user's account:
    - GET: Shows withdrawal form (account number pre-filled)
    - POST: Processes withdrawal and updates account balance
    
    Args:
        request: HTTP request object
        
    Returns:
        - If successful: Redirects to home page
        - Otherwise: Shows withdrawal form with errors
    """
    # Get logged-in account
    account = request.account
    
    # Check if form was submitted
    if request.method == 'POST':
        # Create form with submitted data
        form = WithdrawalForm(request.POST, account=account)
        
        # Validate form
        if form.is_valid():
            # Get cleaned data
            amount = form.cleaned_data['amount']
            description = form.cleaned_data.get('description', '')
            
            # ========== PERFORM WITHDRAWAL ==========
            # Use account's withdraw method (checks balance automatically)
            if account.withdraw(amount):
                # Withdrawal successful
                
                # ========== CREATE TRANSACTION RECORD ==========
                Transaction.objects.create(
                    transaction_type='Withdrawal',
                    amount=amount,
                    from_account=account,  # Account losing money
                    description=description if description else 'Withdrawal',
                    balance_after_transaction=account.balance,
                    status='Completed'
                )
                
                # Show success message
                messages.success(request, f'Successfully withdrew ${amount} from your account. New balance: ${account.balance}')
                return redirect('accounts:home')
            else:
                # Withdrawal failed (insufficient balance or inactive account)
                messages.error(request, 'Withdrawal failed! Insufficient balance or account inactive.')
    else:
        # GET request: Show withdrawal form with account pre-filled
        form = WithdrawalForm(account=account)
    
    # Render withdrawal form template
    return render(request, 'transactions/withdraw.html', {'form': form, 'account': account})


@login_required
def transfer(request):
    """
    Transfer money from logged-in account to another account view
    
    This view handles moving money from the logged-in account to another:
    - GET: Shows transfer form (from account pre-filled)
    - POST: Processes transfer using database transaction for safety
    
    Uses database transactions to ensure both accounts are updated
    atomically (all or nothing) to prevent data corruption.
    
    Args:
        request: HTTP request object
        
    Returns:
        - If successful: Redirects to home page
        - Otherwise: Shows transfer form with errors
    """
    # Get logged-in account (source account)
    from_account = request.account
    
    # Check if form was submitted
    if request.method == 'POST':
        # Create form with submitted data
        form = TransferForm(request.POST, from_account=from_account)
        
        # Validate form
        if form.is_valid():
            # Get cleaned data
            to_account_number = form.cleaned_data['to_account_number']
            amount = form.cleaned_data['amount']
            description = form.cleaned_data.get('description', '')
            
            try:
                # ========== USE DATABASE TRANSACTION ==========
                # This ensures both account updates happen together
                # If anything fails, both changes are rolled back
                with transaction.atomic():
                    # Lock both accounts for update (prevents concurrent modifications)
                    from_account_locked = Account.objects.select_for_update().get(
                        account_number=from_account.account_number, 
                        status='Active'
                    )
                    to_account = Account.objects.select_for_update().get(
                        account_number=to_account_number, 
                        status='Active'
                    )
                    
                    # ========== VALIDATE BALANCE ==========
                    # Double-check balance (form already checked, but be extra safe)
                    if from_account_locked.balance < amount:
                        messages.error(request, 'Insufficient balance!')
                        form = TransferForm(from_account=from_account)
                        return render(request, 'transactions/transfer.html', {'form': form, 'account': from_account})
                    
                    # ========== PERFORM TRANSFER ==========
                    # Withdraw from source account
                    from_account_locked.withdraw(amount)
                    # Deposit to destination account
                    to_account.deposit(amount)
                    
                    # ========== CREATE TRANSACTION RECORD ==========
                    Transaction.objects.create(
                        transaction_type='Transfer',
                        amount=amount,
                        from_account=from_account_locked,
                        to_account=to_account,
                        description=description if description else f'Transfer to {to_account_number}',
                        balance_after_transaction=from_account_locked.balance,  # Balance of source account
                        status='Completed'
                    )
                    
                    # Show success message
                    messages.success(
                        request, 
                        f'Successfully transferred ${amount} to account {to_account_number}. '
                        f'Your new balance: ${from_account_locked.balance}'
                    )
                    # Redirect to home page
                    return redirect('accounts:home')
                    
            except Account.DoesNotExist:
                # Destination account not found
                messages.error(request, 'Destination account not found or inactive!')
    else:
        # GET request: Show transfer form with from account pre-filled
        form = TransferForm(from_account=from_account)
    
    # Render transfer form template
    return render(request, 'transactions/transfer.html', {'form': form, 'account': from_account})


@login_required
def transaction_history(request, account_number=None):
    """
    View transaction history for logged-in account
    
    This view shows all transactions (deposits, withdrawals, transfers)
    involving the logged-in account.
    
    Args:
        request: HTTP request object
        account_number: Account number from URL (optional, uses logged-in account)
        
    Returns:
        Rendered HTML template with transaction list
    """
    # Get logged-in account
    account = request.account
    
    # If account_number provided, verify it matches logged-in account
    if account_number and account_number != account.account_number:
        messages.error(request, 'You can only view your own transaction history.')
        account_number = account.account_number
    
    # ========== GET ALL TRANSACTIONS ==========
    # Import Q for OR queries
    from django.db.models import Q
    
    # Find all transactions where this account is involved
    # Either as sender (from_account) or receiver (to_account)
    transactions = Transaction.objects.filter(
        Q(from_account=account) |  # Account sent money
        Q(to_account=account)      # Account received money
    ).order_by('-created_at')  # Order by newest first
    
    # Render template with account and transactions
    return render(request, 'transactions/transaction_history.html', {
        'account': account,
        'transactions': transactions
    })


@login_required
def all_transactions(request):
    """
    View all transactions for logged-in account
    
    This view shows all transactions for the logged-in account.
    Can be filtered by transaction type.
    
    Args:
        request: HTTP request object
        
    Returns:
        Rendered HTML template with transactions
    """
    # Get logged-in account
    account = request.account
    
    # Get all transactions for this account, ordered by newest first
    from django.db.models import Q
    transactions = Transaction.objects.filter(
        Q(from_account=account) | Q(to_account=account)
    ).order_by('-created_at')
    
    # ========== FILTER BY TRANSACTION TYPE ==========
    # Get filter parameter from URL (e.g., ?type=Deposit)
    transaction_type = request.GET.get('type', '')
    
    # If filter is specified, apply it
    if transaction_type:
        transactions = transactions.filter(transaction_type=transaction_type)
    
    # Render template with transactions and current filter
    return render(request, 'transactions/all_transactions.html', {
        'account': account,
        'transactions': transactions,
        'transaction_type': transaction_type  # Pass to template to show in dropdown
    })
