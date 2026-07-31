from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse



from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError





class Expense(models.Model):

    CATEGORY_CHOICES = [
        ("Food", "Food"),
        ("Transport", "Transport"),
        ("Shopping", "Shopping"),
        ("Bills", "Bills"),
        ("Entertainment", "Entertainment"),
        ("Health", "Health"),
        ("Education", "Education"),
        ("Investment", "Investment"),
        ("Savings", "Savings"),
        ("Other", "Other"),
    ]

    CURRENCY_CHOICES = [
        ("NGN", "Nigerian Naira (₦)"),
        ("USD", "US Dollar ($)"),
        ("EUR", "Euro (€)"),
        ("GBP", "British Pound (£)"),
        ("CAD", "Canadian Dollar (C$)"),
        ("AUD", "Australian Dollar (A$)"),
        ("JPY", "Japanese Yen (¥)"),
        ("INR", "Indian Rupee (₹)"),
        ("CNY", "Chinese Yuan (¥)"),
        ("ZAR", "South African Rand (R)"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="expenses",
    )

    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES,
        default="Other",
    )

    currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default="NGN",
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    description = models.CharField(
        max_length=200,
    )

    receipt = models.ImageField(
        upload_to="receipts/",
        blank=True,
        null=True,
    )

    date = models.DateField()

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return (
            f"{self.get_category_display()} - "
            f"{self.amount} {self.currency}"
        )

    def get_absolute_url(self):
        return reverse("expense_list")

    @property
    def currency_symbol(self):
        symbols = {
            "NGN": "₦",
            "USD": "$",
            "EUR": "€",
            "GBP": "£",
            "CAD": "C$",
            "AUD": "A$",
            "JPY": "¥",
            "INR": "₹",
            "CNY": "¥",
            "ZAR": "R",
        }
        return symbols.get(self.currency, "")



    
class Income(models.Model):

    INCOME_CHOICES = [
        ("SALARY", "Salary"),
        ("BUSINESS", "Business"),
        ("FREELANCE", "Freelance"),
        ("INVESTMENT", "Investment"),
        ("BONUS", "Bonus"),
        ("GIFT", "Gift"),
        ("REFUND", "Refund"),
        ("RENTAL", "Rental Income"),
        ("SIDE_HUSTLE", "Side Hustle"),
        ("OTHER", "Other"),
    ]

    CURRENCY_CHOICES = [
        ("USD", "US Dollar ($)"),
        ("NGN", "Nigerian Naira (₦)"),
        ("EUR", "Euro (€)"),
        ("GBP", "British Pound (£)"),
        ("CAD", "Canadian Dollar (C$)"),
        ("AUD", "Australian Dollar (A$)"),
        ("JPY", "Japanese Yen (¥)"),
        ("INR", "Indian Rupee (₹)"),
        ("CNY", "Chinese Yuan (¥)"),
        ("ZAR", "South African Rand (R)"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="incomes",
    )

    source = models.CharField(
        max_length=20,
        choices=INCOME_CHOICES,
        default="OTHER",
    )

    currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default="USD",
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    description = models.CharField(
        max_length=200,
        blank=True,
    )

    receipt = models.ImageField(
        upload_to="income_receipts/",
        blank=True,
        null=True,
    )

    date = models.DateField()

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"{self.get_source_display()} - {self.amount} {self.currency}"

    def get_absolute_url(self):
        return reverse("income_list") 
    
    
    
    

class Budget(models.Model):

    CATEGORY_CHOICES = [
        ("Food", "Food"),
        ("Transport", "Transport"),
        ("Shopping", "Shopping"),
        ("Bills", "Bills"),
        ("Entertainment", "Entertainment"),
        ("Health", "Health"),
        ("Education", "Education"),
        ("Investment", "Investment"),
        ("Savings", "Savings"),
        ("Other", "Other"),
    ]

    CURRENCY_CHOICES = [
        ("NGN", "₦ Nigerian Naira"),
        ("USD", "$ US Dollar"),
        ("EUR", "€ Euro"),
        ("GBP", "£ British Pound"),
        ("CAD", "C$ Canadian Dollar"),
        ("AUD", "A$ Australian Dollar"),
        ("JPY", "¥ Japanese Yen"),
        ("INR", "₹ Indian Rupee"),
        ("CNY", "¥ Chinese Yuan"),
        ("ZAR", "R South African Rand"),
    ]

    MONTH_CHOICES = [
        (1, "January"),
        (2, "February"),
        (3, "March"),
        (4, "April"),
        (5, "May"),
        (6, "June"),
        (7, "July"),
        (8, "August"),
        (9, "September"),
        (10, "October"),
        (11, "November"),
        (12, "December"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="budgets"
    )

    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES
    )

    currency = models.CharField(
        max_length=5,
        choices=CURRENCY_CHOICES,
        default="NGN"
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    month = models.PositiveSmallIntegerField(
        choices=MONTH_CHOICES
    )

    year = models.PositiveIntegerField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        ordering = ["-year", "-month", "category"]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "user",
                    "category",
                    "currency",
                    "month",
                    "year",
                ],
                name="unique_budget_per_month"
            )
        ]

    def clean(self):

        if self.amount <= 0:
            raise ValidationError(
                "Budget amount must be greater than zero."
            )

    @property
    def month_name(self):
        return dict(self.MONTH_CHOICES).get(self.month)

    def __str__(self):
        return (
            f"{self.user.username} - "
            f"{self.category} "
            f"({self.month_name} {self.year})"
        )    
        

        

class Notification(models.Model):

    TYPE_CHOICES = [
        ("success", "Success"),
        ("info", "Information"),
        ("warning", "Warning"),
        ("danger", "Danger"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications",
    )

    title = models.CharField(
        max_length=200,
    )

    message = models.TextField()

    notification_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default="info",
    )

    is_read = models.BooleanField(
        default=False,
    )

    link = models.CharField(
        max_length=255,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:

        ordering = ["-created_at"]

    def __str__(self):

        return f"{self.user.username} - {self.title}"

    def get_absolute_url(self):

        if self.link:

            return self.link

        return reverse("notification_list")           