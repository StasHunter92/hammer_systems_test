import re

from django import forms
from django.core.exceptions import ValidationError


# ----------------------------------------------------------------------------------------------------------------------
# Create forms
class UserSignupLoginForm(forms.Form):
    """
    Form for login page
    """
    phone_number = forms.CharField(
        max_length=12
    )

    def clean_phone_number(self) -> str:
        """
        Check field using regular expressions
        Returns:
            checked string or raise error
        """
        phone_number = self.cleaned_data['phone_number']

        if not re.match(r'^[+][7][\d]{10}$', phone_number):
            raise ValidationError('Incorrect phone number')

        return phone_number


# ------------------------------------------------------------------------------
class UserAuthenticationForm(forms.Form):
    """
    Form for authenticate page
    """
    password = forms.CharField(
        widget=forms.PasswordInput
    )

    def clean_password(self) -> str:
        """
        Check field using regular expressions
        Returns:
            checked string or raise error
        """
        password = self.cleaned_data['password']

        if not len(password) == 4:
            raise ValidationError('Password must have only 4 digits')
        elif not re.match(r'^\d{4}$', password):
            raise ValidationError('Password must have digits only')

        return password


# ------------------------------------------------------------------------------
class UserProfileForm(forms.Form):
    """
    Form for profile page
    """
    first_name = forms.CharField(
        required=False
    )
    last_name = forms.CharField(
        required=False
    )
    email = forms.EmailField(
        required=False
    )


# ------------------------------------------------------------------------------
class InviteCodeForm(forms.Form):
    """
    Form for invite code field (profile page)
    """
    invited_by_code = forms.CharField(
        max_length=6
    )
