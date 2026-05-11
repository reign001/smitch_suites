from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
from datetime import datetime

from .models import MenuItem, RestaurantOrder, RestaurantOrderItem
from .forms import MenuItemForm, RestaurantOrderForm, RestaurantOrderItemForm
from reception.models import GuestCharge


@login_required
def restaurant_dashboard(request):
    today = timezone.localdate()

    total_orders_today = RestaurantOrder.objects.filter(created_at__date=today).count()
    sales_today = RestaurantOrder.objects.filter(created_at__date=today).aggregate(
        total=Sum('total_amount')
    )['total'] or 0

    unpaid_orders = RestaurantOrder.objects.filter(payment_status='UNPAID').count()
    room_bill_orders = RestaurantOrder.objects.filter(payment_status='ADDED_TO_ROOM').count()

    return render(request, 'restaurant/dashboard.html', {
        'total_orders_today': total_orders_today,
        'sales_today': sales_today,
        'unpaid_orders': unpaid_orders,
        'room_bill_orders': room_bill_orders,
    })


@login_required
def menu_list(request):
    menu_items = MenuItem.objects.all().order_by('name')
    return render(request, 'restaurant/menu_list.html', {'menu_items': menu_items})


@login_required
def add_menu_item(request):
    if request.method == 'POST':
        form = MenuItemForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Menu item added successfully.')
            return redirect('restaurant:menu_list')
    else:
        form = MenuItemForm()

    return render(request, 'restaurant/add_menu_item.html', {'form': form})


@login_required
def order_list(request):
    orders = RestaurantOrder.objects.select_related('booking', 'booking__guest').order_by('-created_at')
    return render(request, 'restaurant/order_list.html', {'orders': orders})


@login_required
def create_order(request):
    if request.method == 'POST':
        order_form = RestaurantOrderForm(request.POST)
        item_form = RestaurantOrderItemForm(request.POST)

        if order_form.is_valid() and item_form.is_valid():
            order = order_form.save(commit=False)
            order.created_by = request.user

            if order.booking:
                order.customer_name = order.booking.guest.full_name
                order.room_number = order.booking.room.room_number

            order.save()

            order_item = item_form.save(commit=False)
            order_item.order = order
            order_item.save()

            order.calculate_total()

            messages.success(request, 'Restaurant order created successfully.')
            return redirect('restaurant:order_detail', order.id)
    else:
        order_form = RestaurantOrderForm()
        item_form = RestaurantOrderItemForm()

    return render(request, 'restaurant/create_order.html', {
        'order_form': order_form,
        'item_form': item_form,
    })


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(
        RestaurantOrder.objects.select_related('booking', 'booking__guest'),
        id=order_id
    )

    return render(request, 'restaurant/order_detail.html', {'order': order})


@login_required
def add_order_to_room_bill(request, order_id):
    order = get_object_or_404(RestaurantOrder, id=order_id)

    if not order.booking:
        messages.error(request, 'This order is not attached to any lodging guest.')
        return redirect('restaurant:order_detail', order.id)

    if order.added_to_guest_bill:
        messages.error(request, 'This restaurant order has already been added to the guest bill.')
        return redirect('restaurant:order_detail', order.id)

    GuestCharge.objects.create(
        booking=order.booking,
        category='RESTAURANT',
        item_name=f'Restaurant Order #{order.id}',
        quantity=1,
        unit_price=order.total_amount,
        total_amount=order.total_amount,
        added_by=request.user
    )

    order.payment_status = 'ADDED_TO_ROOM'
    order.added_to_guest_bill = True
    order.save()

    messages.success(request, 'Restaurant order added to guest room bill.')
    return redirect('restaurant:order_detail', order.id)


@login_required
def restaurant_report(request):
    selected_date = request.GET.get('date')

    if selected_date:
        selected_date_obj = datetime.strptime(selected_date, '%Y-%m-%d').date()
    else:
        selected_date_obj = timezone.localdate()
        selected_date = selected_date_obj.strftime('%Y-%m-%d')

    orders = RestaurantOrder.objects.filter(created_at__date=selected_date_obj).order_by('-created_at')

    total_sales = orders.aggregate(total=Sum('total_amount'))['total'] or 0
    paid_total = orders.filter(payment_status='PAID').aggregate(total=Sum('total_amount'))['total'] or 0
    room_bill_total = orders.filter(payment_status='ADDED_TO_ROOM').aggregate(total=Sum('total_amount'))['total'] or 0
    unpaid_total = orders.filter(payment_status='UNPAID').aggregate(total=Sum('total_amount'))['total'] or 0

    return render(request, 'restaurant/report.html', {
        'selected_date': selected_date,
        'orders': orders,
        'total_sales': total_sales,
        'paid_total': paid_total,
        'room_bill_total': room_bill_total,
        'unpaid_total': unpaid_total,
    })


@login_required
def download_restaurant_report_pdf(request):
    selected_date = request.GET.get('date')

    if selected_date:
        selected_date_obj = datetime.strptime(selected_date, '%Y-%m-%d').date()
    else:
        selected_date_obj = timezone.localdate()
        selected_date = selected_date_obj.strftime('%Y-%m-%d')

    orders = RestaurantOrder.objects.filter(created_at__date=selected_date_obj).order_by('-created_at')

    html = get_template('restaurant/report_pdf.html').render({
        'selected_date': selected_date,
        'orders': orders,
        'total_sales': orders.aggregate(total=Sum('total_amount'))['total'] or 0,
        'paid_total': orders.filter(payment_status='PAID').aggregate(total=Sum('total_amount'))['total'] or 0,
        'room_bill_total': orders.filter(payment_status='ADDED_TO_ROOM').aggregate(total=Sum('total_amount'))['total'] or 0,
        'unpaid_total': orders.filter(payment_status='UNPAID').aggregate(total=Sum('total_amount'))['total'] or 0,
        'generated_at': timezone.now(),
        'generated_by': request.user,
    })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="restaurant_report_{selected_date}.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Error generating restaurant report PDF', status=500)

    return response