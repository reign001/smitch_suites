from django.shortcuts import render

# Create your views here.
from datetime import datetime

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa

from reception.models import Payment, GuestCharge
from restaurant.models import RestaurantOrder
from bar.models import BarSale
from housekeeping.models import LaundryRequest

from .models import (
    Expense,
    FinancialTransaction,
)

from .forms import ExpenseForm


@login_required
def finance_dashboard(request):
    today = timezone.localdate()

    accommodation_income = Payment.objects.filter(
        payment_date__date=today
    ).aggregate(total=Sum('amount'))['total'] or 0

    restaurant_income = RestaurantOrder.objects.filter(
        created_at__date=today
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    bar_income = BarSale.objects.filter(
        created_at__date=today
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    laundry_income = LaundryRequest.objects.filter(
        delivered_at__date=today
    ).aggregate(total=Sum('amount'))['total'] or 0

    total_income = (
        accommodation_income +
        restaurant_income +
        bar_income +
        laundry_income
    )

    total_expenses = Expense.objects.filter(
        expense_date__date=today
    ).aggregate(total=Sum('amount'))['total'] or 0

    net_balance = total_income - total_expenses

    return render(request, 'finances/dashboard.html', {
        'today': today,
        'accommodation_income': accommodation_income,
        'restaurant_income': restaurant_income,
        'bar_income': bar_income,
        'laundry_income': laundry_income,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_balance': net_balance,
    })


@login_required
def expense_list(request):
    expenses = Expense.objects.select_related('category').order_by('-expense_date')

    return render(request, 'finances/expense_list.html', {
        'expenses': expenses
    })


@login_required
def create_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)

        if form.is_valid():
            expense = form.save(commit=False)
            expense.created_by = request.user
            expense.save()

            FinancialTransaction.objects.create(
                source=expense.title,
                transaction_type='EXPENSE',
                amount=expense.amount,
                reference=f'Expense #{expense.id}'
            )

            messages.success(request, 'Expense recorded successfully.')

            return redirect('finances:expense_list')
    else:
        form = ExpenseForm()

    return render(request, 'finances/create_expense.html', {
        'form': form
    })

@login_required
def transaction_list(request):
    transactions = FinancialTransaction.objects.order_by('-created_at')

    return render(request, 'finances/transaction_list.html', {
        'transactions': transactions
    })


@login_required
def daily_finance_report(request):
    selected_date = request.GET.get('date')

    if selected_date:
        report_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
    else:
        report_date = timezone.localdate()
        selected_date = report_date.strftime('%Y-%m-%d')

    accommodation_income = Payment.objects.filter(
        payment_date__date=report_date
    ).aggregate(total=Sum('amount'))['total'] or 0

    restaurant_income = RestaurantOrder.objects.filter(
        created_at__date=report_date
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    bar_income = BarSale.objects.filter(
        created_at__date=report_date
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    laundry_income = LaundryRequest.objects.filter(
        delivered_at__date=report_date
    ).aggregate(total=Sum('amount'))['total'] or 0

    total_income = (
        accommodation_income +
        restaurant_income +
        bar_income +
        laundry_income
    )

    expenses = Expense.objects.filter(expense_date__date=report_date)

    total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or 0

    net_balance = total_income - total_expenses

    return render(request, 'finances/daily_report.html', {
        'selected_date': selected_date,
        'expenses': expenses,
        'accommodation_income': accommodation_income,
        'restaurant_income': restaurant_income,
        'bar_income': bar_income,
        'laundry_income': laundry_income,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_balance': net_balance,
    })


@login_required
def download_daily_finance_report_pdf(request):
    selected_date = request.GET.get('date')

    if selected_date:
        report_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
    else:
        report_date = timezone.localdate()
        selected_date = report_date.strftime('%Y-%m-%d')

    accommodation_income = Payment.objects.filter(
        payment_date__date=report_date
    ).aggregate(total=Sum('amount'))['total'] or 0

    restaurant_income = RestaurantOrder.objects.filter(
        created_at__date=report_date
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    bar_income = BarSale.objects.filter(
        created_at__date=report_date
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    laundry_income = LaundryRequest.objects.filter(
        delivered_at__date=report_date
    ).aggregate(total=Sum('amount'))['total'] or 0

    total_income = (
        accommodation_income +
        restaurant_income +
        bar_income +
        laundry_income
    )

    expenses = Expense.objects.filter(expense_date__date=report_date)

    total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or 0

    net_balance = total_income - total_expenses

    html = get_template('finances/daily_report_pdf.html').render({
        'selected_date': selected_date,
        'generated_at': timezone.now(),
        'generated_by': request.user,
        'expenses': expenses,
        'accommodation_income': accommodation_income,
        'restaurant_income': restaurant_income,
        'bar_income': bar_income,
        'laundry_income': laundry_income,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_balance': net_balance,
    })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="finance_report.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)

    return response