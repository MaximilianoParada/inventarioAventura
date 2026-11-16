from django import forms
from django.db.models import Q

from .models import Category, Experience


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ExperienceForm(forms.ModelForm):
    scheduled_at = forms.DateTimeField(
        label='Fecha y hora',
        input_formats=['%Y-%m-%dT%H:%M'],
        widget=forms.DateTimeInput(
            format='%Y-%m-%dT%H:%M',
            attrs={'class': 'form-control', 'type': 'datetime-local'},
        ),
    )

    class Meta:
        model = Experience
        fields = ['title', 'description', 'price', 'capacity', 'scheduled_at', 'category', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categories = Category.objects.filter(is_active=True)
        if self.instance.pk and self.instance.category_id:
            categories = Category.objects.filter(
                Q(is_active=True) | Q(pk=self.instance.category_id)
            )
        self.fields['category'].queryset = categories.order_by('name')
