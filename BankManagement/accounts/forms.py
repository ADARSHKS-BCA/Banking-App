from django import forms
from .models import Account


class AccountForm(forms.ModelForm):
    pin = forms.CharField(
        widget=forms.PasswordInput(attrs={'maxlength': '4', 'pattern': '[0-9]{4}'}),
        min_length=4,
        max_length=4,
        help_text="Enter a 4-digit PIN"
    )
    confirm_pin = forms.CharField(
        widget=forms.PasswordInput(attrs={'maxlength': '4', 'pattern': '[0-9]{4}'}),
        min_length=4,
        max_length=4,
        label="Confirm PIN"
    )
    
    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 
                  'date_of_birth', 'account_type', 'pin']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        pin = cleaned_data.get('pin')
        confirm_pin = cleaned_data.get('confirm_pin')
        
        if pin and confirm_pin:
            if pin != confirm_pin:
                raise forms.ValidationError("PINs do not match!")
            if not pin.isdigit():
                raise forms.ValidationError("PIN must contain only digits!")
        
        return cleaned_data
    
    def save(self, commit=True):
        account = super().save(commit=False)
        if commit:
            account.save()
        return account


class AccountLoginForm(forms.Form):
    account_number = forms.CharField(max_length=12, label="Account Number")
    pin = forms.CharField(
        widget=forms.PasswordInput(attrs={'maxlength': '4'}),
        max_length=4,
        label="PIN"
    )

