from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Expense, Income,Budget
#
from django import forms
from django.core.exceptions import ValidationError
from datetime import datetime



class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = [
            "category",
            "currency",
            "amount",
            "description",
            "receipt",
            "date",
        ]

        widgets = {
            "category": forms.Select(attrs={
                "class": "form-select"
            }),

            "currency": forms.Select(attrs={
                "class": "form-select"
            }),

            "amount": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Enter amount"
            }),

            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Describe this expense..."
            }),

            "receipt": forms.ClearableFileInput(attrs={
                "class": "form-control",
                "accept": "image/*"
            }),

            "date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date"
            }),
        }


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "Enter your email"
        })
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password1",
            "password2",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Choose a username"
        })

        self.fields["password1"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Create a password"
        })

        self.fields["password2"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Confirm your password"
        })
        
        
        
class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = [
            "source",
            "currency",
            "amount",
            "description",
            "receipt",
            "date",
        ]

        widgets = {
            "source": forms.Select(attrs={
                "class": "form-select"
            }),

            "currency": forms.Select(attrs={
                "class": "form-select"
            }),

            "amount": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Enter income amount"
            }),

            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Describe this income..."
            }),

            "receipt": forms.ClearableFileInput(attrs={
                "class": "form-control"
            }),

            "date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date"
            }),
        }        
        
        
        
class BudgetForm(forms.ModelForm):

    class Meta:

        model = Budget

        fields = [
            "category",
            "currency",
            "amount",
            "month",
            "year",
        ]

        widgets = {

            "category": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "currency": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "amount": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter budget amount",
                    "min": "0",
                    "step": "0.01",
                }
            ),

            "month": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "year": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "2024",
                    "max": "2100",
                }
            ),

        }  
        
    def __init__(self, *args, **kwargs):

        self.user = kwargs.pop("user", None)

        super().__init__(*args, **kwargs)

        # Default year to current year
        if not self.instance.pk:
            self.fields["year"].initial = datetime.now().year

        # Better labels
        self.fields["category"].label = "Budget Category"
        self.fields["currency"].label = "Currency"
        self.fields["amount"].label = "Budget Amount"
        self.fields["month"].label = "Budget Month"
        self.fields["year"].label = "Budget Year"

    def clean_amount(self):

        amount = self.cleaned_data.get("amount")

        if amount is None or amount <= 0:
            raise ValidationError(
                "Budget amount must be greater than zero."
            )

        return amount

    def clean(self):

        cleaned_data = super().clean()

        category = cleaned_data.get("category")
        currency = cleaned_data.get("currency")
        month = cleaned_data.get("month")
        year = cleaned_data.get("year")

        if all([self.user, category, currency, month, year]):

            budget = Budget.objects.filter(
                user=self.user,
                category=category,
                currency=currency,
                month=month,
                year=year,
            )

            # Ignore current record when editing
            if self.instance.pk:
                budget = budget.exclude(pk=self.instance.pk)

            if budget.exists():
                raise ValidationError(
                    "A budget already exists for this category, currency and month."
                )

        return cleaned_data    