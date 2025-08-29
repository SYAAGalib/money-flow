from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from .models import Transaction, Category
from django.utils import timezone
from django.db import models


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label='Confirm Password')
    full_name = forms.CharField()

    class Meta:
        model = User
        fields = ['full_name', 'email', 'password']

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email already registered')
        return email

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('password') != cleaned.get('password_confirm'):
            self.add_error('password_confirm', 'Passwords do not match')
        return cleaned

    def save(self, commit=True):
        full_name = self.cleaned_data['full_name']
        first, *rest = full_name.split(' ', 1)
        user = User(username=self.cleaned_data['email'], email=self.cleaned_data['email'])
        user.first_name = first
        user.last_name = rest[0] if rest else ''
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Improve widget types & placeholders for clarity and proper mobile keyboards
        self.fields['full_name'].widget.attrs.update({
            'placeholder': 'Full name',
            'autocomplete': 'name',
            'aria-label': 'Full name',
        })
        self.fields['email'].widget = forms.EmailInput(attrs={
            'placeholder': 'Email address',
            'autocomplete': 'email',
            'aria-label': 'Email address',
            'inputmode': 'email'
        })
        self.fields['password'].widget.attrs.update({
            'placeholder': 'Password',
            'autocomplete': 'new-password',
            'aria-label': 'Password'
        })
        self.fields['password_confirm'].widget.attrs.update({
            'placeholder': 'Confirm password',
            'autocomplete': 'new-password',
            'aria-label': 'Confirm password'
        })
        self._apply_tailwind()

    def _apply_tailwind(self):
        base = 'w-full px-3 py-2 rounded-md border border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500/40 focus:border-blue-500 dark:bg-slate-700 dark:border-slate-600 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-400 transition-colors'
        for name, field in self.fields.items():
            existing = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = (existing + ' ' + base).strip()


class TransactionForm(forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), initial=timezone.now().date)

    class Meta:
        model = Transaction
        fields = ['type', 'category', 'amount', 'date', 'notes']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = Category.objects.filter(models.Q(user=user) | models.Q(is_default=True)).order_by('name')
        self._apply_tailwind()

    def _apply_tailwind(self):
        for name, field in self.fields.items():
            if field.widget.__class__.__name__ == 'HiddenInput':
                continue
            base = 'w-full px-3 py-2 rounded border border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500/40 focus:border-blue-500 dark:bg-slate-700 dark:border-slate-600 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-400'
            existing = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = (existing + ' ' + base).strip()


class CategoryForm(forms.ModelForm):
    new_category = forms.CharField(required=True, label='')

    class Meta:
        model = Category
        fields = ['name']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # We use a separate visible field new_category; hide name
        self.fields['name'].widget = forms.HiddenInput()
    # Tailwind class for new_category (handled in template input)

    def clean(self):
        cleaned = super().clean()
        name = self.data.get('new_category', '').strip()
        if not name:
            raise forms.ValidationError('Category name required')
        if Category.objects.filter(name__iexact=name, user=self.user).exists():
            raise forms.ValidationError('You already have this category')
        cleaned['name'] = name
        self.cleaned_data['name'] = name
        return cleaned


class StyledAuthenticationForm(AuthenticationForm):
    """Authentication form with Tailwind styling and better placeholders."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Early normalize: if user typed an email, convert to username (which is stored as email lowercased)
        if self.data:
            ident = self.data.get('username', '')
            if ident and '@' in ident:
                from django.contrib.auth import get_user_model
                UserModel = get_user_model()
                try:
                    user_obj = UserModel.objects.get(email__iexact=ident.strip())
                except UserModel.DoesNotExist:
                    user_obj = None
                if user_obj:
                    if hasattr(self.data, '_mutable'):
                        was = self.data._mutable; self.data._mutable = True
                        self.data['username'] = user_obj.get_username()
                        self.data._mutable = was
                    else:
                        try:
                            self.data['username'] = user_obj.get_username()
                        except Exception:
                            pass
        # Rename label to Email if project uses email-as-username pattern
        if 'username' in self.fields:
            self.fields['username'].label = 'Email'
            self.fields['username'].widget.attrs.update({
                'placeholder': 'Email address',
                'autocomplete': 'email',
                'aria-label': 'Email address',
                'inputmode': 'email',
                'autofocus': True
            })
        if 'password' in self.fields:
            self.fields['password'].widget.attrs.update({
                'placeholder': 'Password',
                'autocomplete': 'current-password',
                'aria-label': 'Password'
            })
        base = 'w-full px-3 py-2 rounded-md border border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500/40 focus:border-blue-500 dark:bg-slate-700 dark:border-slate-600 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-400 transition-colors'
        for field in self.fields.values():
            existing = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = (existing + ' ' + base).strip()

    def clean(self):
        # Default AuthenticationForm clean now that normalization happened in __init__
        return super().clean()
