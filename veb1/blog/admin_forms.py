from django import forms
from django.contrib import admin
from .models import Product, Order


class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'cols': 80}),
        }


class OrderAdminForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = '__all__'
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3, 'cols': 80}),
        }