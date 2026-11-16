from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm

from .models import Role, User, UserRole

class LoginForm(AuthenticationForm):
    
    username = forms.CharField(
        label='Username',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingresa tu nombre de usuario'})
    )
    
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Ingresa tu contraseña'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'password']


class StaffUserCreationForm(UserCreationForm):
    role = forms.ModelChoiceField(queryset=Role.objects.all(), label='Rol')

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            UserRole.objects.get_or_create(user_id=user, role=self.cleaned_data['role'])
        return user


class StaffUserUpdateForm(forms.ModelForm):
    role = forms.ModelChoiceField(queryset=Role.objects.all(), required=False, label='Rol')

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'is_active', 'role')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = (
                'form-check-input' if isinstance(field.widget, forms.CheckboxInput) else 'form-control'
            )
        assignment = UserRole.objects.filter(user_id=self.instance).select_related('role').first()
        if assignment:
            self.fields['role'].initial = assignment.role

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            UserRole.objects.filter(user_id=user).delete()
            role = self.cleaned_data.get('role')
            if role:
                UserRole.objects.get_or_create(user_id=user, role=role)
        return user