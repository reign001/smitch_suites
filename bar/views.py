from django.shortcuts import render

# Create your views here.
from datetime import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
from reception.models import GuestCharge
from .models import BarItem, BarSale
from .forms import BarItemForm, BarSaleForm, BarSaleItemForm


@login_required
def bar_dashboard(request):
    today = timezone.localdate()

    sales_today = BarSale.objects.filter(created_at__date=today)
    total_sales_today = sales_today.aggregate(total=Sum('total_amount'))['total'] or 0

    return render(request, 'bar/dashboard.html', {
        'sales_count_today': sales_today.count(),
        'total_sales_today': total_sales_today,
        'unpaid_sales': BarSale.objects.filter(payment_status='UNPAID').count(),
        'room_bill_sales': BarSale.objects.filter(payment_status='ADDED_TO_ROOM').count(),
    })


@login_required
def bar_item_list(request):
    items = BarItem.objects.select_related('inventory_item').order_by('name')
    return render(request, 'bar/bar_item_list.html', {'items': items})


@login_required
def add_bar_item(request):
    if request.method == 'POST':
        form = BarItemForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bar item added successfully.')
            return redirect('bar:bar_item_list')
    else:
        form = BarItemForm()

    return render(request, 'bar/add_bar_item.html', {'form': form})


@login_required
def sale_list(request):
    sales = BarSale.objects.select_related('booking', 'booking__guest').order_by('-created_at')
    return render(request, 'bar/sale_list.html', {'sales': sales})


@login_required
def create_sale(request):
    if request.method == 'POST':
        sale_form = BarSaleForm(request.POST)
        item_form = BarSaleItemForm(request.POST)

        if sale_form.is_valid() and item_form.is_valid():
            sale = sale_form.save(commit=False)
            sale.created_by = request.user

            if sale.booking:
                sale.customer_name = sale.booking.guest.full_name
                sale.room_number = sale.booking.room.room_number

            sale.save()

            sale_item = item_form.save(commit=False)
            sale_item.sale = sale
            sale_item.save()

            sale.calculate_total()

            # Deduct from inventory if linked
            if sale_item.bar_item.inventory_item:
                inv_item = sale_item.bar_item.inventory_item
                if inv_item.quantity_in_stock >= sale_item.quantity:
                    inv_item.quantity_in_stock -= sale_item.quantity
                    inv_item.save()
                else:
                    messages.error(request, 'Warning: inventory stock is lower than quantity sold.')

            messages.success(request, 'Bar sale created successfully.')
            return redirect('bar:sale_detail', sale.id)
    else:
        sale_form = BarSaleForm()
        item_form = BarSaleItemForm()

    return render(request, 'bar/create_sale.html', {
        'sale_form': sale_form,
        'item_form': item_form,
    })


@login_required
def sale_detail(request, sale_id):
    sale = get_object_or_404(
        BarSale.objects.select_related('booking', 'booking__guest'),
        id=sale_id
    )

    return render(request, 'bar/sale_detail.html', {'sale': sale})


@login_required
def add_sale_to_room_bill(request, sale_id):
    sale = get_object_or_404(BarSale, id=sale_id)

    if not sale.booking:
        messages.error(request, 'This sale is not attached to any lodging guest.')
        return redirect('bar:sale_detail', sale.id)

    if sale.added_to_guest_bill:
        messages.error(request, 'This bar sale has already been added to the guest bill.')
        return redirect('bar:sale_detail', sale.id)

    GuestCharge.objects.create(
        booking=sale.booking,
        category='BAR',
        item_name=f'Bar Sale #{sale.id}',
        quantity=1,
        unit_price=sale.total_amount,
        total_amount=sale.total_amount,
        added_by=request.user
    )

    sale.payment_status = 'ADDED_TO_ROOM'
    sale.added_to_guest_bill = True
    sale.save()

    messages.success(request, 'Bar sale added to guest room bill.')
    return redirect('bar:sale_detail', sale.id)


@login_required
def bar_report(request):
    selected_date = request.GET.get('date')

    if selected_date:
        selected_date_obj = datetime.strptime(selected_date, '%Y-%m-%d').date()
    else:
        selected_date_obj = timezone.localdate()
        selected_date = selected_date_obj.strftime('%Y-%m-%d')

    sales = BarSale.objects.filter(created_at__date=selected_date_obj).order_by('-created_at')

    return render(request, 'bar/report.html', {
        'selected_date': selected_date,
        'sales': sales,
        'total_sales': sales.aggregate(total=Sum('total_amount'))['total'] or 0,
        'paid_total': sales.filter(payment_status='PAID').aggregate(total=Sum('total_amount'))['total'] or 0,
        'room_bill_total': sales.filter(payment_status='ADDED_TO_ROOM').aggregate(total=Sum('total_amount'))['total'] or 0,
        'unpaid_total': sales.filter(payment_status='UNPAID').aggregate(total=Sum('total_amount'))['total'] or 0,
    })


@login_required
def download_bar_report_pdf(request):
    selected_date = request.GET.get('date')

    if selected_date:
        selected_date_obj = datetime.strptime(selected_date, '%Y-%m-%d').date()
    else:
        selected_date_obj = timezone.localdate()
        selected_date = selected_date_obj.strftime('%Y-%m-%d')

    sales = BarSale.objects.filter(created_at__date=selected_date_obj).order_by('-created_at')

    html = get_template('bar/report_pdf.html').render({
        'selected_date': selected_date,
        'sales': sales,
        'total_sales': sales.aggregate(total=Sum('total_amount'))['total'] or 0,
        'paid_total': sales.filter(payment_status='PAID').aggregate(total=Sum('total_amount'))['total'] or 0,
        'room_bill_total': sales.filter(payment_status='ADDED_TO_ROOM').aggregate(total=Sum('total_amount'))['total'] or 0,
        'unpaid_total': sales.filter(payment_status='UNPAID').aggregate(total=Sum('total_amount'))['total'] or 0,
        'generated_at': timezone.now(),
        'generated_by': request.user,
    })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="bar_report_{selected_date}.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Error generating bar report PDF', status=500)

    return response