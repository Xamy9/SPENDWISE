




from decimal import Decimal
from django.db.models import Sum

from .models import Budget, Expense, Notification




def create_notifications(
    *,
    user,
    title,
    message,
    notification_type="info",
    link="",
):
    """
    Create a notification for a user.
    """

    return Notification.objects.create(
        user=user,
        title=title,
        message=message,
        notification_type=notification_type,
        link=link,
    )
    
    

def check_budget_notifications(expense):
    """
    Check whether an expense causes a budget warning or budget exceeded
    notification.
    """

    try:
        
        print("Expense category:", expense.category)

        budget = Budget.objects.get(
            
            user=expense.user,
            category=expense.category,
            currency=expense.currency,
            month=expense.date.month,
            year=expense.date.year,
            
        )
        print("Budget found")

    except Budget.DoesNotExist:
        return

    spent = (
        Expense.objects.filter(
            user=expense.user,
            category=budget.category,
            currency=budget.currency,
            date__year=budget.year,
            date__month=budget.month,
        ).aggregate(
            total=Sum("amount")
        )["total"]
        or Decimal("0.00")
    )

    percentage = (spent / budget.amount) * 100

    # -----------------------------
    # Budget Exceeded
    # -----------------------------

    if percentage >= 100:

        if not Notification.objects.filter(
            user=expense.user,
            title="Budget Exceeded",
            message__icontains=budget.category,
            is_read=False,
        ).exists():

            create_notifications(
                user=expense.user,
                title="Budget Exceeded",
                message=(
                    f"Your {budget.category} budget "
                    f"for {budget.month_name} {budget.year} "
                    "has been exceeded."
                ),
                notification_type="danger",
                link=f"/budgets/{budget.pk}/",
            )

    # -----------------------------
    # Budget Warning
    # -----------------------------

    elif percentage >= 80:

        if not Notification.objects.filter(
            user=expense.user,
            title="Budget Almost Reached",
            message__icontains=budget.category,
            is_read=False,
        ).exists():

            create_notifications(
                user=expense.user,
                title="Budget Almost Reached",
                message=(
                    f"You have used "
                    f"{round(percentage, 1)}% "
                    f"of your {budget.category} budget."
                ),
                notification_type="warning",
                link=f"/budgets/{budget.pk}/",
            )    