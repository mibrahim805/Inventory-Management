from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import Product, Purchase, Sale


class RegistrationForm(UserCreationForm):
    class Meta:
        model=User
        fields=["username" ,"email","password1","password2"]


class ProductForm(forms.ModelForm):
    class Meta:
        model=Product
        fields=["name","description","price"]


class PurchaseForm(forms.ModelForm):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['product'].queryset = Product.objects.filter(user=user)

    class Meta:
        model=Purchase
        fields=["product","quantity"]

class SaleForm(forms.ModelForm):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['product'].queryset = Product.objects.filter(user=user)
    class Meta:
        model=Sale
        fields=["product","quantity"]
