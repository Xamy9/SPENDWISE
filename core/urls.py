from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/add/', views.expense_add, name='expense_add'),
    path('expenses/<int:pk>/edit/', views.expense_edit, name='expense_edit'),
    path('expenses/<int:pk>/delete/', views.expense_delete, name='expense_delete'),
    path('register/', views.register, name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path("dashboard/", views.dashboard, name="dashboard"),
    
    # ==========================
    # Income URLs
    # ==========================

    path(
        "income/",
        views.income_list,
        name="income_list",
    ),

    path(
        "income/add/",
        views.income_add,
        name="income_add",
    ),

    path(
        "income/<int:pk>/edit/",
        views.income_edit,
        name="income_edit",
    ),

    path(
        "income/<int:pk>/delete/",
        views.income_delete,
        name="income_delete",
    ),
    
    
    # ===========================
# Budget URLs
# ===========================

path(
    "budgets/",
    views.budget_list,
    name="budget_list",
),

path(
    "budgets/add/",
    views.budget_add,
    name="budget_add",
),

path(
    "budgets/<int:pk>/",
    views.budget_detail,
    name="budget_detail",
),

path(
    "budgets/<int:pk>/edit/",
    views.budget_edit,
    name="budget_edit",
),

path(
    "budgets/<int:pk>/delete/",
    views.budget_delete,
    name="budget_delete",
),


path(
    "notifications/",
    views.notification_list,
    name="notification_list",
),

path(
    "notifications/<int:pk>/read/",
    views.notification_read,
    name="notification_read",
),

path(
    "notifications/read-all/",
    views.notification_read_all,
    name="notification_read_all",
),

path(
    "notifications/<int:pk>/delete/",
    views.notification_delete,
    name="notification_delete",
),


path(
    "notifications/data/",
    views.notification_data,
    name="notification_data",
),



]