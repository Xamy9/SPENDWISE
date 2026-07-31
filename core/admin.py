

from django.contrib import admin
from . models import Expense
from .models import Budget

from .models import Notification



admin.site.register(Expense)
@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "category",
        "currency",
        "amount",
        "month",
        "year",
        "created_at",
    )

    list_filter = (
        "category",
        "currency",
        "month",
        "year",
    )

    search_fields = (
        "user__username",
        "category",
        "currency",
    )

    ordering = (
        "-year",
        "-month",
        "category",
    )

    list_per_page = 20

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (

        ("Budget Information", {
            "fields": (
                "user",
                "category",
                "currency",
                "amount",
            )
        }),

        ("Period", {
            "fields": (
                "month",
                "year",
            )
        }),

        ("System Information", {
            "fields": (
                "created_at",
                "updated_at",
            ),
            "classes": ("collapse",)
        }),

    )
    
    
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "user",
        "notification_type",
        "is_read",
        "created_at",
    )

    list_filter = (
        "notification_type",
        "is_read",
        "created_at",
    )

    search_fields = (
        "title",
        "message",
        "user__username",
    )

    ordering = (
        "-created_at",
    )

    readonly_fields = (
        "created_at",
    )    