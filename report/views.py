from django.shortcuts import render

# Create your views here.
from datetime import datetime, timedelta

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa

from reception.models import Guest, Booking, Room, CheckIn, CheckOut, Payment, GuestCharge
from inventory.models import InventoryItem, StockIn, StockOut
from restaurant.models import RestaurantOrder
from bar.models import BarSale
from housekeeping.models import LaundryRequest, RoomCleaning, LostAndFound, MaintenanceIssue
from finances.models import Expense


def get_date_range(period, selected_date):
    base_date = datetime.strptime(selected_date, '%Y-%m-%d').date()

    if period == 'day':
        start_date = base_date
        end_date = base_date

    elif period == 'week':
        start_date = base_date - timedelta(days=base_date.weekday())
        end_date = start_date + timedelta(days=6)

    elif period == 'month':
        start_date = base_date.replace(day=1)

        if start_date.month == 12:
            next_month = start_date.replace(year=start_date.year + 1, month=1, day=1)
        else:
            next_month = start_date.replace(month=start_date.month + 1, day=1)

        end_date = next_month - timedelta(days=1)

    else:
        start_date = base_date
        end_date = base_date

    return start_date, end_date


def build_general_report(period, selected_date):
    start_date, end_date = get_date_range(period, selected_date)

    guests = Guest.objects.filter(
        created_at__date__range=[start_date, end_date]
    ).order_by('-created_at')

    bookings = Booking.objects.select_related('guest', 'room').filter(
        created_at__date__range=[start_date, end_date]
    ).order_by('-created_at')

    checkins = CheckIn.objects.select_related(
        'booking',
        'booking__guest',
        'booking__room'
    ).filter(
        check_in_time__date__range=[start_date, end_date]
    )

    checkouts = CheckOut.objects.select_related(
        'booking',
        'booking__guest',
        'booking__room'
    ).filter(
        check_out_time__date__range=[start_date, end_date]
    )

    payments = Payment.objects.select_related(
        'booking',
        'booking__guest',
        'booking__room',
        'received_by'
    ).filter(
        payment_date__date__range=[start_date, end_date]
    ).order_by('-payment_date')

    guest_charges = GuestCharge.objects.select_related(
        'booking',
        'booking__guest',
        'booking__room'
    ).filter(
        created_at__date__range=[start_date, end_date]
    ).order_by('-created_at')

    restaurant_orders = RestaurantOrder.objects.filter(
        created_at__date__range=[start_date, end_date]
    )

    bar_sales = BarSale.objects.filter(
        created_at__date__range=[start_date, end_date]
    )

    laundry_requests = LaundryRequest.objects.filter(
        created_at__date__range=[start_date, end_date]
    )

    expenses = Expense.objects.select_related('category').filter(
        expense_date__date__range=[start_date, end_date]
    ).order_by('-expense_date')

    stock_ins = StockIn.objects.select_related('item').filter(
        date_received__date__range=[start_date, end_date]
    )

    stock_outs = StockOut.objects.select_related('item').filter(
        date_issued__date__range=[start_date, end_date]
    )

    cleaning_tasks = RoomCleaning.objects.select_related('room').filter(
        created_at__date__range=[start_date, end_date]
    )

    lost_found = LostAndFound.objects.select_related('room').filter(
        found_at__date__range=[start_date, end_date]
    )

    maintenance_issues = MaintenanceIssue.objects.select_related('room').filter(
        reported_at__date__range=[start_date, end_date]
    )

    total_payments = payments.aggregate(total=Sum('amount'))['total'] or 0
    total_guest_charges = guest_charges.aggregate(total=Sum('total_amount'))['total'] or 0
    restaurant_income = restaurant_orders.aggregate(total=Sum('total_amount'))['total'] or 0
    bar_income = bar_sales.aggregate(total=Sum('total_amount'))['total'] or 0
    laundry_income = laundry_requests.aggregate(total=Sum('amount'))['total'] or 0

    total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or 0

    total_income = total_payments + restaurant_income + bar_income + laundry_income
    net_balance = total_income - total_expenses

    rooms = Room.objects.all()

    return {
        'period': period,
        'selected_date': selected_date,
        'start_date': start_date,
        'end_date': end_date,

        'guests': guests,
        'bookings': bookings,
        'checkins': checkins,
        'checkouts': checkouts,
        'payments': payments,
        'guest_charges': guest_charges,
        'restaurant_orders': restaurant_orders,
        'bar_sales': bar_sales,
        'laundry_requests': laundry_requests,
        'expenses': expenses,
        'stock_ins': stock_ins,
        'stock_outs': stock_outs,
        'cleaning_tasks': cleaning_tasks,
        'lost_found': lost_found,
        'maintenance_issues': maintenance_issues,
        'rooms': rooms,

        'total_guests': guests.count(),
        'total_bookings': bookings.count(),
        'total_checkins': checkins.count(),
        'total_checkouts': checkouts.count(),

        'total_rooms': rooms.count(),
        'available_rooms': rooms.filter(status='AVAILABLE').count(),
        'occupied_rooms': rooms.filter(status='OCCUPIED').count(),
        'reserved_rooms': rooms.filter(status='RESERVED').count(),
        'dirty_rooms': rooms.filter(status='DIRTY').count(),
        'maintenance_rooms': rooms.filter(status='MAINTENANCE').count(),

        'total_payments': total_payments,
        'total_guest_charges': total_guest_charges,
        'restaurant_income': restaurant_income,
        'bar_income': bar_income,
        'laundry_income': laundry_income,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_balance': net_balance,

        'inventory_items': InventoryItem.objects.all().order_by('name'),
    }


@login_required
def report_dashboard(request):
    today = timezone.localdate().strftime('%Y-%m-%d')

    return render(request, 'report/dashboard.html', {
        'selected_date': today,
    })


@login_required
def generate_report(request):
    period = request.GET.get('period', 'day')
    selected_date = request.GET.get('date')

    if not selected_date:
        selected_date = timezone.localdate().strftime('%Y-%m-%d')

    report_data = build_general_report(period, selected_date)

    return render(request, 'report/generated_report.html', report_data)


@login_required
def download_report_pdf(request):
    period = request.GET.get('period', 'day')
    selected_date = request.GET.get('date')

    if not selected_date:
        selected_date = timezone.localdate().strftime('%Y-%m-%d')

    report_data = build_general_report(period, selected_date)

    html = get_template('report/report_pdf.html').render({
        **report_data,
        'generated_at': timezone.now(),
        'generated_by': request.user,
    })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="smitch_suites_{period}_report_{selected_date}.pdf"'
    )

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Error generating PDF report', status=500)

    return response