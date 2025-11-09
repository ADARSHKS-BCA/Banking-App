from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from .models import Transaction
from accounts.models import Account
from .forms import DepositForm, WithdrawalForm, TransferForm


def deposit(request):
    """Deposit money into an account"""
    if request.method == 'POST':
        form = DepositForm(request.POST)
        if form.is_valid():
            account_number = form.cleaned_data['account_number']
            amount = form.cleaned_data['amount']
            description = form.cleaned_data.get('description', '')
            
            try:
                account = Account.objects.get(account_number=account_number, status='Active')
                
                # Perform deposit
                account.deposit(amount)
                
                # Create transaction record
                Transaction.objects.create(
                    transaction_type='Deposit',
                    amount=amount,
                    to_account=account,
                    description=description or f'Deposit of {amount}',
                    balance_after_transaction=account.balance,
                    status='Completed'
                )
                
                messages.success(request, f'Successfully deposited {amount} to account {account_number}. New balance: {account.balance}')
                return redirect('account_detail', account_number=account_number)
            except Account.DoesNotExist:
                messages.error(request, 'Account not found!')
    else:
        form = DepositForm()
    
    return render(request, 'transactions/deposit.html', {'form': form})


def withdraw(request):
    """Withdraw money from an account"""
    if request.method == 'POST':
        form = WithdrawalForm(request.POST)
        if form.is_valid():
            account_number = form.cleaned_data['account_number']
            amount = form.cleaned_data['amount']
            description = form.cleaned_data.get('description', '')
            
            try:
                account = Account.objects.get(account_number=account_number, status='Active')
                
                # Perform withdrawal
                if account.withdraw(amount):
                    # Create transaction record
                    Transaction.objects.create(
                        transaction_type='Withdrawal',
                        amount=amount,
                        from_account=account,
                        description=description or f'Withdrawal of {amount}',
                        balance_after_transaction=account.balance,
                        status='Completed'
                    )
                    
                    messages.success(request, f'Successfully withdrew {amount} from account {account_number}. New balance: {account.balance}')
                    return redirect('account_detail', account_number=account_number)
                else:
                    messages.error(request, 'Withdrawal failed! Insufficient balance or account inactive.')
            except Account.DoesNotExist:
                messages.error(request, 'Account not found!')
    else:
        form = WithdrawalForm()
    
    return render(request, 'transactions/withdraw.html', {'form': form})


def transfer(request):
    """Transfer money between accounts"""
    if request.method == 'POST':
        form = TransferForm(request.POST)
        if form.is_valid():
            from_account_number = form.cleaned_data['from_account_number']
            to_account_number = form.cleaned_data['to_account_number']
            amount = form.cleaned_data['amount']
            description = form.cleaned_data.get('description', '')
            
            try:
                with transaction.atomic():
                    from_account = Account.objects.select_for_update().get(
                        account_number=from_account_number, 
                        status='Active'
                    )
                    to_account = Account.objects.select_for_update().get(
                        account_number=to_account_number, 
                        status='Active'
                    )
                    
                    # Check balance
                    if from_account.balance < amount:
                        messages.error(request, 'Insufficient balance!')
                        return render(request, 'transactions/transfer.html', {'form': form})
                    
                    # Perform transfer
                    from_account.withdraw(amount)
                    to_account.deposit(amount)
                    
                    # Create transaction record
                    Transaction.objects.create(
                        transaction_type='Transfer',
                        amount=amount,
                        from_account=from_account,
                        to_account=to_account,
                        description=description or f'Transfer of {amount} to {to_account_number}',
                        balance_after_transaction=from_account.balance,
                        status='Completed'
                    )
                    
                    messages.success(
                        request, 
                        f'Successfully transferred {amount} from {from_account_number} to {to_account_number}. '
                        f'Your new balance: {from_account.balance}'
                    )
                    return redirect('account_detail', account_number=from_account_number)
            except Account.DoesNotExist:
                messages.error(request, 'One or both accounts not found!')
    else:
        form = TransferForm()
    
    return render(request, 'transactions/transfer.html', {'form': form})


def transaction_history(request, account_number):
    """View transaction history for an account"""
    account = get_object_or_404(Account, account_number=account_number)
    
    transactions = Transaction.objects.filter(
        Q(from_account=account) | Q(to_account=account)
    ).order_by('-created_at')
    
    return render(request, 'transactions/transaction_history.html', {
        'account': account,
        'transactions': transactions
    })


def all_transactions(request):
    """View all transactions (admin view)"""
    transactions = Transaction.objects.all().order_by('-created_at')
    
    # Filter by transaction type
    transaction_type = request.GET.get('type', '')
    if transaction_type:
        transactions = transactions.filter(transaction_type=transaction_type)
    
    return render(request, 'transactions/all_transactions.html', {
        'transactions': transactions,
        'transaction_type': transaction_type
    })
