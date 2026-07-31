from django.shortcuts import render

from django.contrib.auth.views import LoginView
import requests 
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib import messages
from django.db.models import Sum,Max,Q
from .models import Expense
from .forms import ExpenseForm, RegisterForm
from datetime import datetime
from datetime import date
from collections import defaultdict
from django.core.paginator import Paginator 

from.utils import check_budget_notifications

from.utils import create_notifications

from .models import Expense, Income, Budget,Notification
from .forms import ExpenseForm, IncomeForm,BudgetForm    
from django.http import JsonResponse


from decimal import Decimal
from django.utils import timezone






def home(request):
    return render(request, 'home.html')



@login_required
def expense_list(request):
    expenses = Expense.objects.filter(user=request.user)

    # ======================================
    # Search (description OR category)
    # ======================================

    search_query = request.GET.get("search", "").strip()

    if search_query:
        expenses = expenses.filter(
            Q(description__icontains=search_query) |
            Q(category__icontains=search_query)        # searches stored value (e.g., "FOOD")
        )

    # ======================================
    # Category Filter
    # ======================================

    category = request.GET.get("category", "").strip()
    if category:
        expenses = expenses.filter(category=category)

    # ======================================
    # Currency Filter
    # ======================================

    currency = request.GET.get("currency", "").strip()
    if currency:
        expenses = expenses.filter(currency=currency)

    # ======================================
    # Sorting
    # ======================================

    sort = request.GET.get("sort", "newest")

    if sort == "oldest":
        expenses = expenses.order_by("date", "created_at")
    elif sort == "highest":
        expenses = expenses.order_by("-amount")
    elif sort == "lowest":
        expenses = expenses.order_by("amount")
    elif sort == "category":
        # Group by category, then show newest first within each group
        expenses = expenses.order_by("category", "-date")
    elif sort == "currency":
        # Group by currency, then show newest first within each group
        expenses = expenses.order_by("currency", "-date")
    else:
        expenses = expenses.order_by("-date", "-created_at")

    # ==============================
    # Dashboard Statistics (based on full filtered queryset)
    # ==============================

    today = date.today()

    expense_count = expenses.count()
    highest_expense = expenses.aggregate(highest=Max("amount"))["highest"] or 0

    today_expenses = expenses.filter(date=today)
    today_totals = (
        today_expenses
        .values("currency")
        .annotate(total=Sum("amount"))
        .order_by("currency")
    )

    month_expenses = expenses.filter(
        date__year=today.year,
        date__month=today.month,
    )
    month_totals = (
        month_expenses
        .values("currency")
        .annotate(total=Sum("amount"))
        .order_by("currency")
    )

    # ==============================
    # Category Chart
    # ==============================

    category_data = {}
    for expense in expenses:
        display = expense.get_category_display()
        category_data[display] = category_data.get(display, 0) + float(expense.amount)

    # ==============================
    # Currency Symbols
    # ==============================

    currency_symbols = {
        "USD": "$", "NGN": "₦", "EUR": "€", "GBP": "£",
        "CAD": "C$", "AUD": "A$", "JPY": "¥", "INR": "₹",
        "CNY": "¥", "ZAR": "R",
    }

    # ==============================
    # Totals by Currency
    # ==============================

    currency_totals = (
        expenses
        .values("currency")
        .annotate(total=Sum("amount"))
        .order_by("currency")
    )

    totals = []
    for item in currency_totals:
        totals.append({
            "currency": item["currency"],
            "symbol": currency_symbols.get(item["currency"], ""),
            "total": item["total"],
        })

    # ==============================
    # Today's Totals
    # ==============================

    today_summary = []
    for item in today_totals:
        today_summary.append({
            "currency": item["currency"],
            "symbol": currency_symbols.get(item["currency"], ""),
            "total": item["total"],
        })

    # ==============================
    # This Month Totals
    # ==============================

    month_summary = []
    for item in month_totals:
        month_summary.append({
            "currency": item["currency"],
            "symbol": currency_symbols.get(item["currency"], ""),
            "total": item["total"],
        })

    # ==============================
    # Pagination
    # ==============================

    paginator = Paginator(expenses, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # ==============================
    # Context
    # ==============================

    context = {
        "expenses": page_obj,
        "page_obj": page_obj,

        "category_data": category_data,
        "currency_totals": totals,
        "expense_count": expense_count,
        "highest_expense": highest_expense,
        "today_summary": today_summary,
        "month_summary": month_summary,

        "search_query": search_query,
        "selected_category": category,
        "selected_currency": currency,
        "selected_sort": sort,

        "categories": Expense.CATEGORY_CHOICES,
        "currencies": Expense.CURRENCY_CHOICES,
    }

    return render(request, "expense_list.html", context)



@login_required
def expense_add(request):

    if request.method == "POST":

        form = ExpenseForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():

            expense = form.save(commit=False)

            expense.user = request.user

            expense.save()

            # Automatically check the related budget
            check_budget_notifications(expense)

            messages.success(
                request,
                "Expense added successfully!"
            )

            return redirect("expense_list")

    else:

        form = ExpenseForm()

    return render(
        request,
        "expense_form.html",
        {
            "form": form,
            "title": "Add Expense",
        },
    )



@login_required
def expense_edit(request, pk):

    expense = get_object_or_404(
        Expense,
        pk=pk,
        user=request.user,
    )

    if request.method == "POST":

        form = ExpenseForm(
            request.POST,
            request.FILES,
            instance=expense,
        )

        if form.is_valid():

            expense = form.save()

            # Automatically check the related budget
            check_budget_notifications(expense)

            messages.success(
                request,
                "Expense updated successfully!"
            )

            return redirect("expense_list")

    else:

        form = ExpenseForm(
            instance=expense
        )

    return render(
        request,
        "expense_form.html",
        {
            "form": form,
            "title": "Edit Expense",
        },
    )



@login_required
def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        expense.delete()
        messages.success(request, 'Expense deleted!')
        return redirect('expense_list')
    return render(request, 'expense_confirm_delete.html', {'expense': expense})



def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})



def logout_view(request):
    logout(request)
    messages.info(request, 'Logged out.')
    return redirect('home')


class CustomLoginView(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True
    
    
    
#------------------------
#    INCOME VIEWS    
#-------------------------


@login_required
def income_list(request):
    incomes = (
        Income.objects
        .filter(user=request.user)
        .order_by("-date", "-created_at")
    )

    context = {
        "incomes": incomes,
    }

    return render(
        request,
        "income_list.html",
        context,
    )
    
    
@login_required
def income_add(request):

    if request.method == "POST":

        form = IncomeForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():

            income = form.save(commit=False)

            income.user = request.user

            income.save()

            messages.success(
                request,
                "Income added successfully."
            )

            return redirect("income_list")

    else:

        form = IncomeForm()

    return render(
        request,
        "income_form.html",
        {
            "form": form,
            "title": "Add Income",
        },
    )
    
    
    
@login_required
def income_edit(request, pk):

    income = get_object_or_404(
        Income,
        pk=pk,
        user=request.user,
    )

    if request.method == "POST":

        form = IncomeForm(
            request.POST,
            request.FILES,
            instance=income,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Income updated successfully."
            )

            return redirect("income_list")

    else:

        form = IncomeForm(instance=income)

    return render(
        request,
        "income_form.html",
        {
            "form": form,
            "title": "Edit Income",
        },
    )
    
    
@login_required
def income_delete(request, pk):

    income = get_object_or_404(
        Income,
        pk=pk,
        user=request.user,
    )

    if request.method == "POST":

        income.delete()

        messages.success(
            request,
            "Income deleted successfully."
        )

        return redirect("income_list")

    return render(
        request,
        "income_confirm_delete.html",
        {
            "income": income,
        },
    )
      
     
#===================
#  DASHBOARD VIEW
#====================

@login_required
def dashboard(request):

    # =====================================
    # Querysets
    # =====================================

    expenses = Expense.objects.filter(
        user=request.user
    )

    incomes = Income.objects.filter(
        user=request.user
    )

    today = date.today()

    # =====================================
    # Statistics
    # =====================================

    expense_count = expenses.count()

    income_count = incomes.count()

    total_transactions = (
        expense_count +
        income_count
    )

    highest_expense = (
        expenses.aggregate(
            highest=Max("amount")
        )["highest"] or 0
    )

    highest_income = (
        incomes.aggregate(
            highest=Max("amount")
        )["highest"] or 0
    )

    # =====================================
    # Currency Symbols
    # =====================================

    currency_symbols = {

        "USD": "$",

        "NGN": "₦",

        "EUR": "€",

        "GBP": "£",

        "CAD": "C$",

        "AUD": "A$",

        "JPY": "¥",

        "INR": "₹",

        "CNY": "¥",

        "ZAR": "R",

    }

    # =====================================
    # Income Totals By Currency
    # =====================================

    income_queryset = (

        incomes

        .values("currency")

        .annotate(total=Sum("amount"))

        .order_by("currency")

    )

    income_totals = []

    for item in income_queryset:

        income_totals.append({

            "currency": item["currency"],

            "symbol": currency_symbols.get(
                item["currency"],
                ""
            ),

            "total": item["total"] or 0,

        })

    # =====================================
    # Expense Totals By Currency
    # =====================================

    expense_queryset = (

        expenses

        .values("currency")

        .annotate(total=Sum("amount"))

        .order_by("currency")

    )

    expense_totals = []

    for item in expense_queryset:

        expense_totals.append({

            "currency": item["currency"],

            "symbol": currency_symbols.get(
                item["currency"],
                ""
            ),

            "total": item["total"] or 0,

        })

    # =====================================
    # Today's Income & Expenses
    # =====================================

    today_income_queryset = (

        incomes

        .filter(date=today)

        .values("currency")

        .annotate(total=Sum("amount"))

        .order_by("currency")

    )

    today_expense_queryset = (

        expenses

        .filter(date=today)

        .values("currency")

        .annotate(total=Sum("amount"))

        .order_by("currency")

    )

    # =====================================
    # This Month Income & Expenses
    # =====================================

    month_income_queryset = (

        incomes

        .filter(

            date__year=today.year,

            date__month=today.month,

        )

        .values("currency")

        .annotate(total=Sum("amount"))

        .order_by("currency")

    )

    month_expense_queryset = (

        expenses

        .filter(

            date__year=today.year,

            date__month=today.month,

        )

        .values("currency")

        .annotate(total=Sum("amount"))

        .order_by("currency")

    )
    
        # =====================================
    # Balance Per Currency
    # =====================================

    income_lookup = {
        item["currency"]: item["total"]
        for item in income_totals
    }

    expense_lookup = {
        item["currency"]: item["total"]
        for item in expense_totals
    }

    all_currencies = sorted(
        set(income_lookup.keys()) |
        set(expense_lookup.keys())
    )

    balance_totals = []

    for currency in all_currencies:

        income = income_lookup.get(currency, 0) or 0

        expense = expense_lookup.get(currency, 0) or 0

        balance_totals.append({

            "currency": currency,

            "symbol": currency_symbols.get(
                currency,
                ""
            ),

            "income": income,

            "expense": expense,

            "balance": income - expense,

        })

    # =====================================
    # Today's Summary
    # =====================================

    today_income_summary = []

    for item in today_income_queryset:

        today_income_summary.append({

            "currency": item["currency"],

            "symbol": currency_symbols.get(
                item["currency"],
                ""
            ),

            "total": item["total"] or 0,

        })

    today_expense_summary = []

    for item in today_expense_queryset:

        today_expense_summary.append({

            "currency": item["currency"],

            "symbol": currency_symbols.get(
                item["currency"],
                ""
            ),

            "total": item["total"] or 0,

        })

    # =====================================
    # Monthly Summary
    # =====================================

    month_income_summary = []

    for item in month_income_queryset:

        month_income_summary.append({

            "currency": item["currency"],

            "symbol": currency_symbols.get(
                item["currency"],
                ""
            ),

            "total": item["total"] or 0,

        })

    month_expense_summary = []

    for item in month_expense_queryset:

        month_expense_summary.append({

            "currency": item["currency"],

            "symbol": currency_symbols.get(
                item["currency"],
                ""
            ),

            "total": item["total"] or 0,

        })

    # =====================================
    # Expense Category Chart
    # =====================================

    expense_category_data = {}

    for expense in expenses:

        category = expense.get_category_display()

        expense_category_data[category] = (

            expense_category_data.get(category, 0)

            + float(expense.amount)

        )

    # =====================================
    # Income Source Chart
    # =====================================

    income_source_data = {}

    for income in incomes:

        source = income.get_source_display()

        income_source_data[source] = (

            income_source_data.get(source, 0)

            + float(income.amount)

        )

    # =====================================
    # Recent Transactions
    # =====================================

    recent_expenses = (

        expenses

        .order_by("-date", "-created_at")[:5]

    )

    recent_incomes = (

        incomes

        .order_by("-date", "-created_at")[:5]

    )
   
       # =====================================
    # Context
    # =====================================

    context = {

        # Statistics
        "expense_count": expense_count,
        "income_count": income_count,
        "total_transactions": total_transactions,

        # Highest Records
        "highest_expense": highest_expense,
        "highest_income": highest_income,

        # Totals By Currency
        "income_totals": income_totals,
        "expense_totals": expense_totals,
        "balance_totals": balance_totals,

        # Today's Summary
        "today_income_summary": today_income_summary,
        "today_expense_summary": today_expense_summary,

        # Monthly Summary
        "month_income_summary": month_income_summary,
        "month_expense_summary": month_expense_summary,

        # Charts
        "expense_category_data": expense_category_data,
        "income_source_data": income_source_data,

        # Recent Records
        "recent_expenses": recent_expenses,
        "recent_incomes": recent_incomes,

    }

    return render(
        request,
        "dashboard.html",
        context,
    )
    
    
    
# =====================================
# BUDGET LIST
# =====================================


@login_required
def budget_list(request):

    budgets = (
        Budget.objects
        .filter(user=request.user)
        .order_by("-year", "-month", "category")
    )

    for budget in budgets:

        spent = (
            Expense.objects.filter(
                user=request.user,
                category=budget.category,
                currency=budget.currency,
                date__year=budget.year,
                date__month=budget.month,
            ).aggregate(
                total=Sum("amount")
            )["total"]
            or Decimal("0.00")
        )

        budget.spent = spent
        budget.remaining = budget.amount - spent

        if budget.amount > 0:
            budget.percentage = round(
                (spent / budget.amount) * 100,
                1,
            )
        else:
            budget.percentage = 0

    category_count = (
        budgets.values("category")
        .distinct()
        .count()
    )

    context = {
        "budgets": budgets,
        "category_count": category_count,
        "now": timezone.now(),
    }

    return render(
        request,
        "budget_list.html",
        context,
    )


# =====================================
# ADD BUDGET
# =====================================

@login_required
def budget_add(request):

    if request.method == "POST":

        form = BudgetForm(
            request.POST,
            user=request.user,
        )

        if form.is_valid():

            budget = form.save(commit=False)

            budget.user = request.user

            budget.save()

            messages.success(
                request,
                "Budget created successfully."
            )

            return redirect("budget_list")

    else:

        form = BudgetForm(
            user=request.user
        )

    return render(
        request,
        "budget_form.html",
        {
            "form": form,
            "title": "Add Budget",
        },
    )    
   
   
# =====================================
# BUDGET DETAIL
# =====================================

@login_required
def budget_detail(request, pk):

    budget = get_object_or_404(
        Budget,
        pk=pk,
        user=request.user,
    )

    spent = (
        Expense.objects.filter(
            user=request.user,
            category=budget.category,
            currency=budget.currency,
            date__year=budget.year,
            date__month=budget.month,
        ).aggregate(
            total=Sum("amount")
        )["total"] or 0
    )

    remaining = budget.amount - spent

    percentage = 0

    if budget.amount > 0:
        percentage = round((spent / budget.amount) * 100, 1)

    context = {
        "budget": budget,
        "spent": spent,
        "remaining": remaining,
        "percentage": percentage,
    }

    return render(
        request,
        "budget_detail.html",
        context,
    )


# =====================================
# EDIT BUDGET
# =====================================

@login_required
def budget_edit(request, pk):

    budget = get_object_or_404(
        Budget,
        pk=pk,
        user=request.user,
    )

    if request.method == "POST":

        form = BudgetForm(
            request.POST,
            instance=budget,
            user=request.user,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Budget updated successfully."
            )

            return redirect(
                "budget_list"
            )

    else:

        form = BudgetForm(
            instance=budget,
            user=request.user,
        )

    return render(
        request,
        "budget_form.html",
        {
            "form": form,
            "title": "Edit Budget",
        },
    )   
    
    

# =====================================
# DELETE BUDGET
# =====================================

@login_required
def budget_delete(request, pk):

    budget = get_object_or_404(
        Budget,
        pk=pk,
        user=request.user,
    )

    if request.method == "POST":

        budget.delete()

        messages.success(
            request,
            "Budget deleted successfully."
        )

        return redirect("budget_list")

    return render(
        request,
        "budget_delete.html",
        {
            "budget": budget,
        },
    ) 
    
    
    


@login_required
def notification_list(request):

    notifications = (
        Notification.objects
        .filter(user=request.user)
        .order_by("-created_at")
    )

    unread_count = (
        notifications
        .filter(is_read=False)
        .count()
    )

    context = {
        "notifications": notifications,
        "unread_count": unread_count,
    }

    return render(
        request,
        "notifications.html",
        context,
    )  
    
    
    
@login_required
def notification_read(request, pk):

    notification = get_object_or_404(
        Notification,
        pk=pk,
        user=request.user,
    )

    notification.is_read = True

    notification.save()

    if notification.link:

        return redirect(notification.link)

    return redirect("notification_list")


@login_required
def notification_read_all(request):

    Notification.objects.filter(
        user=request.user,
        is_read=False,
    ).update(
        is_read=True
    )

    messages.success(
        request,
        "All notifications marked as read."
    )

    return redirect("notification_list")


@login_required
def notification_delete(request, pk):

    notification = get_object_or_404(
        Notification,
        pk=pk,
        user=request.user,
    )

    notification.delete()

    messages.success(
        request,
        "Notification deleted successfully."
    )

    return redirect("notification_list")      
    
    
@login_required
def notification_data(request):

    latest_notifications = (
        Notification.objects
        .filter(user=request.user)
        .order_by("-created_at")[:5]
    )

    data = []

    for notification in latest_notifications:

        data.append({
            "id": notification.pk,
            "title": notification.title,
            "message": notification.message,
            "is_read": notification.is_read,
            "type": notification.notification_type,
            "link": notification.link,
            "created_at": notification.created_at.strftime("%b %d, %Y %I:%M %p"),
        })

    return JsonResponse({
        "count": Notification.objects.filter(
            user=request.user,
            is_read=False,
        ).count(),
        "notifications": data,
    })    