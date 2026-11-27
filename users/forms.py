from django import forms
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from mysite.forms import BootstrapFormMixin, validate_image_size

from .models import Campus, Profile, normalize_phone_number


class RegisterForm(BootstrapFormMixin, UserCreationForm):
    email = forms.EmailField(
        label='University email',
        help_text=f'Only @{settings.ALLOWED_EMAIL_DOMAIN} addresses can register. '
                  'We will send an activation link there.',
    )
    campus = forms.ChoiceField(choices=Campus.choices)
    whatsapp_number = forms.CharField(
        label='WhatsApp number',
        max_length=25,
        help_text='Shown on your listings so buyers can contact you. '
                  'Include the country code, e.g. +996 555 123 456.',
    )

    field_order = ['username', 'email', 'campus', 'whatsapp_number', 'password1', 'password2']

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email']

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        domain = settings.ALLOWED_EMAIL_DOMAIN.lower()
        if not email.endswith('@' + domain):
            raise forms.ValidationError(
                f'Please use your university email address (ending in @{domain}).'
            )
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def clean_whatsapp_number(self):
        return normalize_phone_number(self.cleaned_data['whatsapp_number'])

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        # The account stays inactive until the student clicks the link in their email.
        user.is_active = False
        if commit:
            user.save()  # the post_save signal creates the profile
            profile = user.profile
            profile.campus = self.cleaned_data['campus']
            profile.whatsapp_number = self.cleaned_data['whatsapp_number']
            profile.save()
        return user


class LoginForm(BootstrapFormMixin, AuthenticationForm):
    error_messages = {
        **AuthenticationForm.error_messages,
        'invalid_login': 'Wrong username or password. If you just registered, '
                         'activate your account using the link in your university email first.',
    }


class ProfileForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['campus', 'whatsapp_number', 'image']
        labels = {'whatsapp_number': 'WhatsApp number', 'image': 'Profile photo'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['campus'].required = True
        self.fields['whatsapp_number'].required = True

    def clean_whatsapp_number(self):
        return normalize_phone_number(self.cleaned_data['whatsapp_number'])

    def clean_image(self):
        return validate_image_size(self.cleaned_data.get('image'))
