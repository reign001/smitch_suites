from django.shortcuts import render

# Create your views here.
from datetime import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa

from reception.models import GuestCharge, Room

from .models import (
    RoomCleaning,
    LaundryRequest,
    LostAndFound,
    MaintenanceIssue
)

from .forms import (
    RoomCleaningForm,
    LaundryRequestForm,
    LostAndFoundForm,
    MaintenanceIssueForm
)

@login_required
def housekeeping_dashboard(request):
    return render(request, 'housekeeping/dashboard.html', {
        'dirty_rooms': Room.objects.filter(status='DIRTY').count(),
        'cleaning_tasks': RoomCleaning.objects.filter(status='IN_PROGRESS').count(),
        'pending_laundry': LaundryRequest.objects.exclude(status='DELIVERED').count(),
        'maintenance_issues': MaintenanceIssue.objects.filter(status='OPEN').count(),
    })

@login_required
def cleaning_list(request):
    tasks = RoomCleaning.objects.select_related('room', 'assigned_to').order_by('-created_at')

    return render(request, 'housekeeping/cleaning_list.html', {
        'tasks': tasks
    })


@login_required
def create_cleaning_task(request):
    if request.method == 'POST':
        form = RoomCleaningForm(request.POST)

        if form.is_valid():
            task = form.save(commit=False)
            task.status = 'DIRTY'
            task.save()

            task.room.status = 'DIRTY'
            task.room.save()

            messages.success(request, 'Cleaning task created.')
            return redirect('housekeeping:cleaning_list')
    else:
        form = RoomCleaningForm()

    return render(request, 'housekeeping/create_cleaning_task.html', {
        'form': form
    })


@login_required
def start_cleaning(request, task_id):
    task = get_object_or_404(RoomCleaning, id=task_id)

    task.status = 'IN_PROGRESS'
    task.started_at = timezone.now()
    task.save()

    messages.success(request, 'Cleaning started.')
    return redirect('housekeeping:cleaning_list')


@login_required
def complete_cleaning(request, task_id):
    task = get_object_or_404(RoomCleaning, id=task_id)

    task.status = 'CLEANED'
    task.completed_at = timezone.now()
    task.save()

    messages.success(request, 'Cleaning completed.')
    return redirect('housekeeping:cleaning_list')


@login_required
def inspect_cleaning(request, task_id):
    task = get_object_or_404(RoomCleaning, id=task_id)

    task.status = 'AVAILABLE'
    task.inspected_at = timezone.now()
    task.save()

    task.room.status = 'AVAILABLE'
    task.room.save()

    messages.success(request, 'Room inspected and made available.')
    return redirect('housekeeping:cleaning_list')

@login_required
def laundry_list(request):
    requests = LaundryRequest.objects.select_related(
        'booking',
        'booking__guest'
    ).order_by('-created_at')

    return render(request, 'housekeeping/laundry_list.html', {
        'requests': requests
    })


@login_required
def create_laundry_request(request):
    if request.method == 'POST':
        form = LaundryRequestForm(request.POST)

        if form.is_valid():
            laundry = form.save(commit=False)
            laundry.collected_by = request.user
            laundry.save()

            messages.success(request, 'Laundry request created.')
            return redirect('housekeeping:laundry_list')
    else:
        form = LaundryRequestForm()

    return render(request, 'housekeeping/create_laundry_request.html', {
        'form': form
    })


@login_required
def deliver_laundry(request, request_id):
    laundry = get_object_or_404(LaundryRequest, id=request_id)

    if not laundry.added_to_guest_bill:
        GuestCharge.objects.create(
            booking=laundry.booking,
            category='LAUNDRY',
            item_name='Laundry Service',
            quantity=1,
            unit_price=laundry.amount,
            total_amount=laundry.amount,
            added_by=request.user
        )

        laundry.added_to_guest_bill = True

    laundry.status = 'DELIVERED'
    laundry.delivered_at = timezone.now()
    laundry.save()

    messages.success(request, 'Laundry delivered and added to guest bill.')
    return redirect('housekeeping:laundry_list')


@login_required
def lost_found_list(request):
    items = LostAndFound.objects.select_related('room').order_by('-found_at')

    return render(request, 'housekeeping/lost_found_list.html', {
        'items': items
    })


@login_required
def create_lost_found(request):
    if request.method == 'POST':
        form = LostAndFoundForm(request.POST)

        if form.is_valid():
            item = form.save(commit=False)
            item.found_by = request.user
            item.save()

            messages.success(request, 'Lost & found item recorded.')
            return redirect('housekeeping:lost_found_list')
    else:
        form = LostAndFoundForm()

    return render(request, 'housekeeping/create_lost_found.html', {
        'form': form
    })

@login_required
def maintenance_list(request):
    issues = MaintenanceIssue.objects.select_related('room').order_by('-reported_at')

    return render(request, 'housekeeping/maintenance_list.html', {
        'issues': issues
    })


@login_required
def create_maintenance_issue(request):
    if request.method == 'POST':
        form = MaintenanceIssueForm(request.POST)

        if form.is_valid():
            issue = form.save(commit=False)
            issue.reported_by = request.user
            issue.save()

            messages.success(request, 'Maintenance issue reported.')
            return redirect('housekeeping:maintenance_list')
    else:
        form = MaintenanceIssueForm()

    return render(request, 'housekeeping/create_maintenance_issue.html', {
        'form': form
    })


@login_required
def housekeeping_report(request):
    today = timezone.localdate()

    cleaning_completed = RoomCleaning.objects.filter(
        completed_at__date=today
    ).count()

    laundry_completed = LaundryRequest.objects.filter(
        delivered_at__date=today
    ).count()

    maintenance_issues = MaintenanceIssue.objects.filter(
        reported_at__date=today
    ).count()

    return render(request, 'housekeeping/report.html', {
        'today': today,
        'cleaning_completed': cleaning_completed,
        'laundry_completed': laundry_completed,
        'maintenance_issues': maintenance_issues,
    })

@login_required
def download_housekeeping_report_pdf(request):
    today = timezone.localdate()

    html = get_template('housekeeping/report_pdf.html').render({
        'today': today,
        'generated_at': timezone.now(),
        'generated_by': request.user,
        'cleaning_completed': RoomCleaning.objects.filter(
            completed_at__date=today
        ).count(),
        'laundry_completed': LaundryRequest.objects.filter(
            delivered_at__date=today
        ).count(),
        'maintenance_issues': MaintenanceIssue.objects.filter(
            reported_at__date=today
        ).count(),
    })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="housekeeping_report.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)

    return response