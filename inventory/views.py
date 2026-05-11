from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import InventoryItem, StockIn, StockOut, DepartmentRequest
from django.db import models


# @login_required
# def inventory_dashboard(request):
#     total_items = InventoryItem.objects.count()
#     low_stock_items = InventoryItem.objects.filter(
#         quantity_in_stock__lte=models.F('reorder_level')
#     ).count()
#     pending_requests = DepartmentRequest.objects.filter(status='PENDING').count()

#     return render(request, 'inventory/dashboard.html', {
#         'total_items': total_items,
#         'low_stock_items': low_stock_items,
#         'pending_requests': pending_requests,
#     })

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from django.utils import timezone
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa

from .models import InventoryItem, StockIn, StockOut, DepartmentRequest
from .forms import InventoryItemForm, StockInForm, StockOutForm


@login_required
def inventory_dashboard(request):
    total_items = InventoryItem.objects.count()

    low_stock_items = InventoryItem.objects.filter(
        quantity_in_stock__lte=models.F('reorder_level')
    ).count()

    pending_requests = DepartmentRequest.objects.filter(status='PENDING').count()

    total_stock_value = 0
    for item in InventoryItem.objects.all():
        total_stock_value += item.quantity_in_stock * item.unit_cost

    recent_stock_ins = StockIn.objects.select_related('item').order_by('-date_received')[:5]
    recent_stock_outs = StockOut.objects.select_related('item').order_by('-date_issued')[:5]

    return render(request, 'inventory/dashboard.html', {
        'total_items': total_items,
        'low_stock_items': low_stock_items,
        'pending_requests': pending_requests,
        'total_stock_value': total_stock_value,
        'recent_stock_ins': recent_stock_ins,
        'recent_stock_outs': recent_stock_outs,
    })


@login_required
def item_list(request):
    items = InventoryItem.objects.select_related('category', 'supplier').order_by('name')

    return render(request, 'inventory/item_list.html', {
        'items': items
    })


@login_required
def add_item(request):
    if request.method == 'POST':
        form = InventoryItemForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Inventory item added successfully.')
            return redirect('inventory:item_list')
    else:
        form = InventoryItemForm()

    return render(request, 'inventory/add_item.html', {
        'form': form
    })


@login_required
def stock_in(request):
    if request.method == 'POST':
        form = StockInForm(request.POST)

        if form.is_valid():
            stock = form.save(commit=False)
            stock.received_by = request.user
            stock.save()

            messages.success(request, 'Stock added successfully.')
            return redirect('inventory:item_list')
    else:
        form = StockInForm()

    return render(request, 'inventory/stock_in.html', {
        'form': form
    })


@login_required
def stock_out(request):
    if request.method == 'POST':
        form = StockOutForm(request.POST)

        if form.is_valid():
            stock = form.save(commit=False)
            stock.issued_by = request.user

            try:
                stock.save()
                messages.success(request, 'Stock issued successfully.')
                return redirect('inventory:item_list')
            except ValueError as e:
                messages.error(request, str(e))
    else:
        form = StockOutForm()

    return render(request, 'inventory/stock_out.html', {
        'form': form
    })


@login_required
def inventory_report(request):
    items = InventoryItem.objects.select_related('category', 'supplier').order_by('name')

    total_items = items.count()
    low_stock_items = items.filter(quantity_in_stock__lte=models.F('reorder_level')).count()

    total_stock_value = 0
    for item in items:
        total_stock_value += item.quantity_in_stock * item.unit_cost

    return render(request, 'inventory/inventory_report.html', {
        'items': items,
        'total_items': total_items,
        'low_stock_items': low_stock_items,
        'total_stock_value': total_stock_value,
    })


@login_required
def download_inventory_report_pdf(request):
    items = InventoryItem.objects.select_related('category', 'supplier').order_by('name')

    total_items = items.count()
    low_stock_items = items.filter(quantity_in_stock__lte=models.F('reorder_level')).count()

    total_stock_value = 0
    for item in items:
        total_stock_value += item.quantity_in_stock * item.unit_cost

    html = get_template('inventory/inventory_report_pdf.html').render({
        'items': items,
        'total_items': total_items,
        'low_stock_items': low_stock_items,
        'total_stock_value': total_stock_value,
        'generated_at': timezone.now(),
        'generated_by': request.user,
    })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="inventory_report.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Error generating inventory report PDF', status=500)

    return response