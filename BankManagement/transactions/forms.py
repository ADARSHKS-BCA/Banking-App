"""
Transaction Forms - Form classes for transaction operations

These forms handle user input validation for:
- Depositing money
- Withdrawing money
- Transferring money between accounts
"""

from django import forms
from .models import Transaction
from accounts.models import Account


class DepositForm(forms.Form):
    """
    Form for depositing money into an account
    
    This form collects:
    - Account number (where to deposit) - pre-filled if account provided
    - Amount to deposit
    - Optional description
    """
    
    def __init__(self, *args, **kwargs):
        # Get account from kwargs if provided
        account = kwargs.pop('account', None)
        super().__init__(*args, **kwargs)
        
        # If account provided, pre-fill and hide account number field
        if account:
            self.fields['account_number'] = forms.CharField(
                max_length=12,
                label="Account Number",
                initial=account.account_number,
                widget=forms.TextInput(attrs={'readonly': True, 'class': 'form-control-plaintext bg-light'})
            )
        else:
            self.fields['account_number'] = forms.CharField(max_length=12, label="Account Number")
    
    # Amount: Decimal field with minimum value of 0.01 (can't deposit 0 or negative)
    # max_digits=12, decimal_places=2 means max value is 9999999999.99
    amount = forms.DecimalField(max_digits=12, decimal_places=2, min_value=0.01, label="Amount")
    
    # Description: Optional notes about the deposit
    description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),  # Multi-line text input
        required=False,  # Not required
        label="Description (Optional)"
    )
    
    def clean_account_number(self):
        """
        Validate that the account number exists and is active
        
        This method is called automatically during form validation.
        It checks if the account exists in the database and is active.
        
        Returns:
            account_number: The validated account number string
            
        Raises:
            ValidationError: If account doesn't exist or is inactive
        """
        # Get the account number from form data
        account_number = self.cleaned_data.get('account_number')
        
        try:
            # Try to find the account in database
            # Must be active (status='Active')
            account = Account.objects.get(account_number=account_number, status='Active')
            # If found, return the account number
            return account_number
        except Account.DoesNotExist:
            # If account not found or inactive, raise validation error
            raise forms.ValidationError("Account not found or inactive!")


class WithdrawalForm(forms.Form):
    """
    Form for withdrawing money from an account
    
    This form collects:
    - Account number (where to withdraw from) - pre-filled if account provided
    - PIN (for security verification)
    - Amount to withdraw
    - Optional description
    """
    
    def __init__(self, *args, **kwargs):
        # Get account from kwargs if provided
        account = kwargs.pop('account', None)
        super().__init__(*args, **kwargs)
        
        # If account provided, pre-fill and hide account number field
        if account:
            self.fields['account_number'] = forms.CharField(
                max_length=12,
                label="Account Number",
                initial=account.account_number,
                widget=forms.TextInput(attrs={'readonly': True, 'class': 'form-control-plaintext bg-light'})
            )
        else:
            self.fields['account_number'] = forms.CharField(max_length=12, label="Account Number")
    
    # PIN: Required for security (4 digits)
    pin = forms.CharField(
        widget=forms.PasswordInput(attrs={'maxlength': '4'}),  # Hide input
        max_length=4,
        label="PIN"
    )
    
    # Amount: Must be positive and greater than 0.01
    amount = forms.DecimalField(max_digits=12, decimal_places=2, min_value=0.01, label="Amount")
    
    # Description: Optional notes
    description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        label="Description (Optional)"
    )
    
    def clean(self):
        """
        Custom validation for withdrawal form
        
        This method validates:
        1. Account exists and is active
        2. PIN is correct
        3. Account has sufficient balance
        
        Returns:
            cleaned_data: Validated form data
            
        Raises:
            ValidationError: If any validation fails
        """
        # Get cleaned data from parent validation
        cleaned_data = super().clean()
        
        # Extract form values
        account_number = cleaned_data.get('account_number')
        pin = cleaned_data.get('pin')
        amount = cleaned_data.get('amount')
        
        # Only validate if we have account number and PIN
        if account_number and pin:
            try:
                # Find the account
                account = Account.objects.get(account_number=account_number, status='Active')
                
                # Check if PIN matches
                if account.pin != pin:
                    raise forms.ValidationError("Invalid PIN!")
                
                # Check if account has enough balance
                if amount and account.balance < amount:
                    raise forms.ValidationError(f"Insufficient balance! Available: {account.balance}")
                    
            except Account.DoesNotExist:
                # Account doesn't exist or is inactive
                raise forms.ValidationError("Account not found or inactive!")
        
        return cleaned_data


class TransferForm(forms.Form):
    """
    Form for transferring money between accounts
    
    This form collects:
    - From account number (source) - pre-filled if from_account provided
    - To account number (destination)
    - PIN (from the source account)
    - Amount to transfer
    - Optional description
    """
    
    def __init__(self, *args, **kwargs):
        # Get from_account from kwargs if provided
        from_account = kwargs.pop('from_account', None)
        super().__init__(*args, **kwargs)
        
        # If from_account provided, pre-fill and hide from account number field
        if from_account:
            self.fields['from_account_number'] = forms.CharField(
                max_length=12,
                label="From Account Number",
                initial=from_account.account_number,
                widget=forms.TextInput(attrs={'readonly': True, 'class': 'form-control-plaintext bg-light'})
            )
        else:
            self.fields['from_account_number'] = forms.CharField(max_length=12, label="From Account Number")
    
    # To account: The account receiving money
    to_account_number = forms.CharField(max_length=12, label="To Account Number")
    
    # PIN: Required from the "from" account for security
    pin = forms.CharField(
        widget=forms.PasswordInput(attrs={'maxlength': '4'}),
        max_length=4,
        label="PIN"
    )
    
    # Amount: Must be positive
    amount = forms.DecimalField(max_digits=12, decimal_places=2, min_value=0.01, label="Amount")
    
    # Description: Optional notes
    description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        label="Description (Optional)"
    )
    
    def clean(self):
        """
        Custom validation for transfer form
        
        This method validates:
        1. Accounts are different (can't transfer to same account)
        2. From account exists, is active, and PIN is correct
        3. From account has sufficient balance
        4. To account exists and is active
        
        Returns:
            cleaned_data: Validated form data
            
        Raises:
            ValidationError: If any validation fails
        """
        # Get cleaned data
        cleaned_data = super().clean()
        
        # Extract form values
        from_account_number = cleaned_data.get('from_account_number')
        to_account_number = cleaned_data.get('to_account_number')
        pin = cleaned_data.get('pin')
        amount = cleaned_data.get('amount')
        
        # Check if trying to transfer to the same account
        if from_account_number == to_account_number:
            raise forms.ValidationError("Cannot transfer to the same account!")
        
        # Validate "from" account
        if from_account_number and pin:
            try:
                # Find the source account
                from_account = Account.objects.get(account_number=from_account_number, status='Active')
                
                # Verify PIN
                if from_account.pin != pin:
                    raise forms.ValidationError("Invalid PIN!")
                
                # Check balance
                if amount and from_account.balance < amount:
                    raise forms.ValidationError(f"Insufficient balance! Available: {from_account.balance}")
                    
            except Account.DoesNotExist:
                raise forms.ValidationError("From account not found or inactive!")
        
        # Validate "to" account
        if to_account_number:
            try:
                # Find the destination account
                to_account = Account.objects.get(account_number=to_account_number, status='Active')
            except Account.DoesNotExist:
                raise forms.ValidationError("To account not found or inactive!")
        
        return cleaned_data
