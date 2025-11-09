"""
Account Forms - Form classes for account-related operations

These forms handle user input validation for:
- Creating new bank accounts
- Logging into accounts
"""

from django import forms
from .models import Account


class AccountForm(forms.ModelForm):
    """
    Form for creating a new bank account
    
    This form collects all necessary information to create an account:
    - Customer personal information
    - Account type selection
    - PIN creation with confirmation
    """
    
    # PIN field: Custom field for 4-digit PIN
    # PasswordInput widget hides the input as user types
    # maxlength='4' limits input to 4 characters
    # pattern='[0-9]{4}' ensures only digits are entered (HTML5 validation)
    pin = forms.CharField(
        widget=forms.PasswordInput(attrs={'maxlength': '4', 'pattern': '[0-9]{4}'}),
        min_length=4,  # Minimum 4 characters
        max_length=4,  # Maximum 4 characters
        help_text="Enter a 4-digit PIN"
    )
    
    # Confirm PIN field: User must enter PIN twice to prevent typos
    confirm_pin = forms.CharField(
        widget=forms.PasswordInput(attrs={'maxlength': '4', 'pattern': '[0-9]{4}'}),
        min_length=4,
        max_length=4,
        label="Confirm PIN"  # Display label in form
    )
    
    # Profile picture field: Optional image upload for user profile
    profile_picture = forms.ImageField(
        required=False,  # Profile picture is optional
        label="Profile Picture",
        help_text="Upload your profile picture (optional). Accepted formats: JPG, PNG, GIF. Max size: 5MB.",
        widget=forms.FileInput(attrs={
            'accept': 'image/*',  # Only accept image files
            'class': 'form-control'
        })
    )
    
    class Meta:
        """
        Meta class: Tells Django which model and fields to use
        
        - model: The model this form is based on
        - fields: Which fields from the model to include in the form
        - widgets: Custom HTML widgets for specific fields
        """
        model = Account  # This form is for the Account model
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 
                  'date_of_birth', 'account_type', 'profile_picture', 'pin']
        widgets = {
            # Use HTML5 date picker for date of birth
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            # Make address field a textarea with 3 rows
            'address': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean_profile_picture(self):
        """
        Validate profile picture upload
        
        This method validates:
        1. File size (max 5MB)
        2. File type (only images)
        
        Returns:
            profile_picture: The validated image file
            
        Raises:
            ValidationError: If file is too large or wrong type
        """
        profile_picture = self.cleaned_data.get('profile_picture')
        
        # If no picture uploaded, that's fine (it's optional)
        if not profile_picture:
            return profile_picture
        
        # Check file size (5MB = 5 * 1024 * 1024 bytes)
        max_size = 5 * 1024 * 1024  # 5MB in bytes
        if profile_picture.size > max_size:
            raise forms.ValidationError("Image file too large. Maximum size is 5MB.")
        
        # Check file type by extension
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif']
        file_name = profile_picture.name.lower()
        if not any(file_name.endswith(ext) for ext in allowed_extensions):
            raise forms.ValidationError("Invalid file type. Only JPG, PNG, and GIF images are allowed.")
        
        return profile_picture
    
    def clean(self):
        """
        Custom validation method that runs after field validation
        
        This method:
        1. Checks if PIN and confirm PIN match
        2. Validates that PIN contains only digits
        
        Returns:
            cleaned_data: Dictionary of validated form data
            
        Raises:
            ValidationError: If PINs don't match or contain non-digits
        """
        # Get cleaned data from parent class (after field validation)
        cleaned_data = super().clean()
        
        # Get PIN and confirm PIN values
        pin = cleaned_data.get('pin')
        confirm_pin = cleaned_data.get('confirm_pin')
        
        # Only validate if both PINs are provided
        if pin and confirm_pin:
            # Check if PINs match
            if pin != confirm_pin:
                raise forms.ValidationError("PINs do not match!")
            # Check if PIN contains only digits
            if not pin.isdigit():
                raise forms.ValidationError("PIN must contain only digits!")
            # Check if PIN is exactly 4 digits (len() is the correct Python function)
            if len(pin) != 4:
                raise forms.ValidationError("PIN must be 4 digits!")
        
        # Return the cleaned data
        return cleaned_data
    
    def save(self, commit=True):
        """
        Override save method to handle account creation
        
        This method handles saving the account including the profile picture.
        The profile picture is automatically saved to the media/profile_pictures/ directory.
        
        Args:
            commit: If True, save to database immediately
            
        Returns:
            Account: The created Account instance
        """
        # Create account instance but don't save yet (commit=False)
        account = super().save(commit=False)
        # If commit is True, save to database
        if commit:
            account.save()  # This triggers account number generation and saves profile picture
        return account


class AccountLoginForm(forms.Form):
    """
    Form for logging into an account
    
    This form collects:
    - Account number (12 digits)
    - PIN (4 digits)
    
    Note: This is a simple form, not a ModelForm, because we're not
    creating or editing a model, just validating login credentials.
    """
    
    # Account number field: 12-character string
    account_number = forms.CharField(max_length=12, label="Account Number")
    
    # PIN field: 4-digit password input
    pin = forms.CharField(
        widget=forms.PasswordInput(attrs={'maxlength': '4'}),  # Hide input, limit to 4 chars
        max_length=4,
        label="PIN"
    )
