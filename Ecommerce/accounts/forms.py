from django import forms
from .models import CustomUser,ShippingAddress

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'confirm_password']

class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(label='Email')

class VerifyOTPForm(forms.Form):
    otp = forms.CharField(label='OTP')

class SetNewPasswordForm(forms.Form):
    password = forms.CharField(label='New Password', widget=forms.PasswordInput)
    confirm_password = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError("The passwords do not match.")
        

    # def __init__(self, user, *args, **kwargs):
    #     self.user = user
    #     super(SetNewPasswordForm, self).__init__(*args, **kwargs)

    # def clean_password(self):
    #     password = self.cleaned_data.get('password')
    #     if self.user.check_password(password):
    #         raise forms.ValidationError("New password must be different from the previous one.")
    #     return password

    # def clean_confirm_password(self):
    #     password = self.cleaned_data.get('password')
    #     confirm_password = self.cleaned_data.get('confirm_password')
    #     if password and confirm_password and password != confirm_password:
    #         raise forms.ValidationError("Passwords do not match.")
    #     return confirm_password


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = ['full_name',  'phone_number','address_line1', 'address_line2', 'city', 'state', 'postal_code']
