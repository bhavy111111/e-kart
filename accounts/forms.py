from django import forms
from .models import Account,UserProfile

class RegisterationForm(forms.ModelForm):

    password = forms.CharField(widget = forms.PasswordInput(attrs = {
    'placeholder':'Enter Password',
    'class': 'form-control'
    }))
    confirm_password = forms.CharField(widget = forms.PasswordInput(attrs = {
    'placeholder':'Confirm Password',
    'class': 'form-control'
    }))
    '''
    first_name = forms.CharField(widget = forms.PasswordInput(attrs = {
    'placeholder':'Confirm Password',
    'class': 'form-control'
    }))
    last_name = forms.CharField(widget = forms.PasswordInput(attrs = {
    'placeholder':'Enter Last Name',
    'class': 'form-control'
    }))
    email = forms.CharField(widget = forms.EmailField(attrs = {
    'placeholder':'Enter Email',
    'class': 'form-control'
    }))
    phone_number = forms.CharField(widget = forms.PasswordInput(attrs = {
    'placeholder':'Enter Phone Number',
    'class': 'form-control'
    }))
    '''
    class Meta:
        model = Account
        fields = ['first_name' , 'last_name' , 'email','phone_number','password']

    def __init__(self, *args, **kwargs):
        super(RegisterationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter First Name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter last Name'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Enter Phone Number'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter Email Address'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
    def pass_confirm(self):
        cleaned_data = super(RegisterationForm,self).pass_confirm()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if(password != confirm_password):
            raise forms.ValidationError(
            'Password doesnt match!'
            )
class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ('first_name' , 'last_name','phone_number')

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


class UserProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False, error_messages = {'invalid':("Image files only")}, widget=forms.FileInput)
    class Meta:
        model = UserProfile
        fields = ('address_line_1', 'address_line_2', 'city', 'state', 'country', 'profile_picture')

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
