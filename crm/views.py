from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from reception.models import Guest, Booking, Payment, GuestCharge

from .models import (
    GuestCRMProfile,
    GuestComplaint,
    GuestFeedback,
    CorporateClient
)

from .forms import (
    GuestCRMProfileForm,
    GuestComplaintForm,
    GuestFeedbackForm,
    CorporateClientForm
)


@login_required
def crm_dashboard(request):
    total_guests = Guest.objects.count()
    vip_guests = GuestCRMProfile.objects.filter(guest_type='VIP').count()
    corporate_guests = GuestCRMProfile.objects.filter(guest_type='CORPORATE').count()
    blacklisted_guests = GuestCRMProfile.objects.filter(guest_type='BLACKLISTED').count()
    open_complaints = GuestComplaint.objects.filter(status='OPEN').count()
    corporate_clients = CorporateClient.objects.count()

    return render(request, 'crm/dashboard.html', {
        'total_guests': total_guests,
        'vip_guests': vip_guests,
        'corporate_guests': corporate_guests,
        'blacklisted_guests': blacklisted_guests,
        'open_complaints': open_complaints,
        'corporate_clients': corporate_clients,
    })


@login_required
def crm_guest_list(request):
    guests = Guest.objects.all().order_by('-created_at')

    return render(request, 'crm/guest_list.html', {
        'guests': guests
    })


@login_required
def guest_profile_detail(request, guest_id):
    guest = get_object_or_404(Guest, id=guest_id)

    profile, created = GuestCRMProfile.objects.get_or_create(
        guest=guest
    )

    bookings = Booking.objects.filter(guest=guest).order_by('-created_at')
    complaints = GuestComplaint.objects.filter(guest=guest).order_by('-created_at')
    feedbacks = GuestFeedback.objects.filter(guest=guest).order_by('-created_at')

    total_spent = 0
    payments = Payment.objects.filter(booking__guest=guest)
    for payment in payments:
        total_spent += payment.amount

    guest_charges = GuestCharge.objects.filter(booking__guest=guest).order_by('-created_at')

    if request.method == 'POST':
        form = GuestCRMProfileForm(request.POST, instance=profile)

        if form.is_valid():
            form.save()
            messages.success(request, 'Guest CRM profile updated successfully.')
            return redirect('crm:guest_detail', guest.id)
    else:
        form = GuestCRMProfileForm(instance=profile)

    return render(request, 'crm/guest_detail.html', {
        'guest': guest,
        'profile': profile,
        'form': form,
        'bookings': bookings,
        'complaints': complaints,
        'feedbacks': feedbacks,
        'guest_charges': guest_charges,
        'total_spent': total_spent,
    })


@login_required
def complaint_list(request):
    complaints = GuestComplaint.objects.select_related(
        'guest',
        'handled_by'
    ).order_by('-created_at')

    return render(request, 'crm/complaint_list.html', {
        'complaints': complaints
    })


@login_required
def create_complaint(request):
    if request.method == 'POST':
        form = GuestComplaintForm(request.POST)

        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.handled_by = request.user

            if complaint.status == 'RESOLVED':
                complaint.resolved_at = timezone.now()

            complaint.save()

            messages.success(request, 'Complaint recorded successfully.')
            return redirect('crm:complaint_list')
    else:
        form = GuestComplaintForm()

    return render(request, 'crm/create_complaint.html', {
        'form': form
    })


@login_required
def create_feedback(request):
    if request.method == 'POST':
        form = GuestFeedbackForm(request.POST)

        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.recorded_by = request.user
            feedback.save()

            messages.success(request, 'Guest feedback recorded successfully.')
            return redirect('crm:guest_detail', feedback.guest.id)
    else:
        form = GuestFeedbackForm()

    return render(request, 'crm/create_feedback.html', {
        'form': form
    })


@login_required
def corporate_client_list(request):
    clients = CorporateClient.objects.all().order_by('-created_at')

    return render(request, 'crm/corporate_client_list.html', {
        'clients': clients
    })


@login_required
def create_corporate_client(request):
    if request.method == 'POST':
        form = CorporateClientForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Corporate client added successfully.')
            return redirect('crm:corporate_client_list')
    else:
        form = CorporateClientForm()

    return render(request, 'crm/create_corporate_client.html', {
        'form': form
    })