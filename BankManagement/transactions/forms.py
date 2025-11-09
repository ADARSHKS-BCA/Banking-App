from django import forms
from .models import Transaction
from accounts.models import Account


class DepositForm(forms.Form):
    account_number = forms.CharField(max_length=12, label="Account Number")
    amount = forms.DecimalField(max_digits=12, decimal_places=2, min_value=0.01, label="Amount")
    description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        label="Description (Optional)"
    )
    
    def clean_account_number(self):
        account_number = self.cleaned_data.get('account_number')
        try:
            account = Account.objects.get(account_number=account_number, status='Active')
            return account_number
        except Account.DoesNotExist:
            raise forms.ValidationError("Account not found or inactive!")


class WithdrawalForm(forms.Form):
    account_number = forms.CharField(max_length=12, label="Account Number")
    pin = forms.CharField(
        widget=forms.PasswordInput(attrs={'maxlength': '4'}),
        max_length=4,
        label="PIN"
    )
    amount = forms.DecimalField(max_digits=12, decimal_places=2, min_value=0.01, label="Amount")
    description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        label="Description (Optional)"
    )
    
    def clean(self):
        cleaned_data = super().clean()
        account_number = cleaned_data.get('account_number')
        pin = cleaned_data.get('pin')
        amount = cleaned_data.get('amount')
        
        if account_number and pin:
            try:
                account = Account.objects.get(account_number=account_number, status='Active')
                if account.pin != pin:
                    raise forms.ValidationError("Invalid PIN!")
                if amount and account.balance < amount:
                    raise forms.ValidationError(f"Insufficient balance! Available: {account.balance}")
            except Account.DoesNotExist:
                raise forms.ValidationError("Account not found or inactive!")
        
        return cleaned_data


class TransferForm(forms.Form):
    from_account_number = forms.CharField(max_length=12, label="From Account Number")
    to_account_number = forms.CharField(max_length=12, label="To Account Number")
    pin = forms.CharField(
        widget=forms.PasswordInput(attrs={'maxlength': '4'}),
        max_length=4,
        label="PIN"
    )
    amount = forms.DecimalField(max_digits=12, decimal_places=2, min_value=0.01, label="Amount")
    description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        label="Description (Optional)"
    )
    
    def clean(self):
        cleaned_data = super().clean()
        from_account_number = cleaned_data.get('from_account_number')
        to_account_number = cleaned_data.get('to_account_number')
        pin = cleaned_data.get('pin')
        amount = cleaned_data.get('amount')
        
        if from_account_number == to_account_number:
            raise forms.ValidationError("Cannot transfer to the same account!")
        
        if from_account_number and pin:
            try:
                from_account = Account.objects.get(account_number=from_account_number, status='Active')
                if from_account.pin != pin:
                    raise forms.ValidationError("Invalid PIN!")
                if amount and from_account.balance < amount:
                    raise forms.ValidationError(f"Insufficient balance! Available: {from_account.balance}")
            except Account.DoesNotExist:
                raise forms.ValidationError("From account not found or inactive!")
        
        if to_account_number:
            try:
                to_account = Account.objects.get(account_number=to_account_number, status='Active')
            except Account.DoesNotExist:
                raise forms.ValidationError("To account not found or inactive!")
        
        return cleaned_data

