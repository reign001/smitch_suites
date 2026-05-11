from django.shortcuts import render

# Create your views here.
from .models import Booking, CheckIn, Payment
from housekeeping.models import RoomCleaning
from .forms import CheckInForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Room, CheckIn, CheckOut
from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import timedelta
from decimal import Decimal
from .forms import BookingForm
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum
from django.template.loader import get_template
from django.utils import timezone
from .models import RoomServiceRequest, GuestCharge
from .forms import RoomServiceRequestForm
from django.http import HttpResponse
from xhtml2pdf import pisa
from datetime import datetime

from .models import Booking, CheckOut, Payment, GuestCharge
from .forms import CheckOutForm


@login_required
@login_required
def reception_dashboard(request):
    today = timezone.localdate()

    available_rooms = Room.objects.filter(status='AVAILABLE').count()
    occupied_rooms = Room.objects.filter(status='OCCUPIED').count()
    todays_checkins = CheckIn.objects.filter(check_in_time__date=today).count()
    todays_checkouts = CheckOut.objects.filter(check_out_time__date=today).count()

    return render(request, 'reception/dashboard.html', {
        'available_rooms': available_rooms,
        'occupied_rooms': occupied_rooms,
        'todays_checkins': todays_checkins,
        'todays_checkouts': todays_checkouts,
    })


from django.shortcuts import render
from .models import Guest, Room, Booking, Payment, GuestCharge


@login_required
def create_booking(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)

        if form.is_valid():
            room = form.cleaned_data['room']
            check_in_date = form.cleaned_data['check_in_date']
            check_out_date = form.cleaned_data['check_out_date']

            nights = (check_out_date - check_in_date).days

            if nights <= 0:
                messages.error(request, 'Check-out date must be after check-in date.')
                return render(request, 'reception/create_booking.html', {'form': form})

            guest = Guest.objects.create(
                full_name=form.cleaned_data['full_name'],
                phone=form.cleaned_data['phone'],
                email=form.cleaned_data['email'],
                gender=form.cleaned_data['gender'],
                address=form.cleaned_data['address'],
                id_type=form.cleaned_data['id_type'],
                id_number=form.cleaned_data['id_number'],
            )

            total_amount = room.price_per_night * nights

            booking = Booking.objects.create(
                guest=guest,
                room=room,
                booked_by=request.user,
                check_in_date=check_in_date,
                check_out_date=check_out_date,
                number_of_guests=form.cleaned_data['number_of_guests'],
                status='CONFIRMED',
                total_amount=total_amount,
                amount_paid=form.cleaned_data['amount_paid'],
                note=form.cleaned_data['note'],
            )

            room.status = 'RESERVED'
            room.save()

            messages.success(request, 'Booking created successfully.')
            return redirect('reception:booking_detail', booking.id)

    else:
        form = BookingForm()

    return render(request, 'reception/create_booking.html', {
        'form': form
    })




@login_required
def booking_detail(request, booking_id):
    booking = Booking.objects.select_related('guest', 'room', 'booked_by').get(id=booking_id)

    return render(request, 'reception/booking_detail.html', {
        'booking': booking
    })

@login_required
def booking_list(request):
    bookings = Booking.objects.select_related(
        'guest',
        'room',
        'booked_by'
    ).order_by('-created_at')

    return render(request, 'reception/booking_list.html', {
        'bookings': bookings
    })

@login_required
def download_booking_pdf(request, booking_id):
    booking = Booking.objects.select_related(
        'guest',
        'room'
    ).get(id=booking_id)

    template_path = 'reception/booking_pdf.html'

    context = {
        'booking': booking
    }

    response = HttpResponse(content_type='application/pdf')

    response['Content-Disposition'] = (
        f'attachment; filename="booking_{booking.id}.pdf"'
    )

    template = get_template(template_path)

    html = template.render(context)

    pisa_status = pisa.CreatePDF(
        html,
        dest=response
    )

    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)

    return response


@login_required
def check_in_guest(request):
    bookings = Booking.objects.select_related('guest', 'room').filter(
        status='CONFIRMED'
    ).order_by('check_in_date')

    return render(request, 'reception/check_in_guest.html', {
        'bookings': bookings
    })

@login_required
def process_check_in(request, booking_id):
    booking = Booking.objects.select_related('guest', 'room').get(id=booking_id)

    if booking.status == 'CHECKED_IN':
        messages.error(request, 'This guest has already been checked in.')
        return redirect('reception:booking_detail', booking.id)

    if booking.status == 'CHECKED_OUT':
        messages.error(request, 'This booking has already been checked out.')
        return redirect('reception:booking_detail', booking.id)

    if request.method == 'POST':
        form = CheckInForm(request.POST)

        if form.is_valid():
            additional_payment = form.cleaned_data.get('additional_payment') or 0
            payment_method = form.cleaned_data.get('payment_method')
            payment_reference = form.cleaned_data.get('payment_reference')
            note = form.cleaned_data.get('note')

            CheckIn.objects.create(
                booking=booking,
                checked_in_by=request.user,
                note=note
            )

            if additional_payment > 0:
                Payment.objects.create(
                    booking=booking,
                    received_by=request.user,
                    amount=additional_payment,
                    payment_method=payment_method,
                    reference=payment_reference,
                    note='Payment made during check-in'
                )

                booking.amount_paid += additional_payment

            booking.status = 'CHECKED_IN'
            booking.save()

            booking.room.status = 'OCCUPIED'
            booking.room.save()

            messages.success(request, 'Guest checked in successfully.')
            return redirect('reception:booking_detail', booking.id)

    else:
        form = CheckInForm()

    return render(request, 'reception/process_check_in.html', {
        'booking': booking,
        'form': form
    })




@login_required
def room_list(request):
    rooms = Room.objects.all().order_by('room_number')

    total_rooms = rooms.count()
    available_rooms = rooms.filter(status='AVAILABLE').count()
    reserved_rooms = rooms.filter(status='RESERVED').count()
    occupied_rooms = rooms.filter(status='OCCUPIED').count()
    dirty_rooms = rooms.filter(status='DIRTY').count()
    maintenance_rooms = rooms.filter(status='MAINTENANCE').count()

    return render(request, 'reception/room_list.html', {
        'rooms': rooms,
        'total_rooms': total_rooms,
        'available_rooms': available_rooms,
        'reserved_rooms': reserved_rooms,
        'occupied_rooms': occupied_rooms,
        'dirty_rooms': dirty_rooms,
        'maintenance_rooms': maintenance_rooms,
    })


@login_required
def download_rooms_pdf(request):
    rooms = Room.objects.all().order_by('room_number')

    context = {
        'rooms': rooms,
        'total_rooms': rooms.count(),
        'available_rooms': rooms.filter(status='AVAILABLE').count(),
        'reserved_rooms': rooms.filter(status='RESERVED').count(),
        'occupied_rooms': rooms.filter(status='OCCUPIED').count(),
        'dirty_rooms': rooms.filter(status='DIRTY').count(),
        'maintenance_rooms': rooms.filter(status='MAINTENANCE').count(),
    }

    template = get_template('reception/rooms_pdf.html')
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="room_status_report.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Error generating room PDF', status=500)

    return response


@login_required
def mark_room_clean(request, room_id):
    room = get_object_or_404(Room, id=room_id)

    if room.status == 'DIRTY':
        room.status = 'AVAILABLE'
        room.save()
        messages.success(request, f'Room {room.room_number} has been marked as clean and available.')
    else:
        messages.error(request, f'Room {room.room_number} is not currently dirty.')

    return redirect('reception:room_list')


@login_required
def guest_list(request):
    selected_date = request.GET.get('date')

    guests = Guest.objects.all().order_by('-created_at')

    if selected_date:
        guests = guests.filter(created_at__date=selected_date)

    return render(request, 'reception/guest_list.html', {
        'guests': guests,
        'selected_date': selected_date,
    })

@login_required
def download_guest_list_pdf(request):
    selected_date = request.GET.get('date')

    guests = Guest.objects.all().order_by('-created_at')

    if selected_date:
        guests = guests.filter(created_at__date=selected_date)

    template = get_template('reception/guest_list_pdf.html')

    html = template.render({
        'guests': guests,
        'selected_date': selected_date,
    })

    response = HttpResponse(content_type='application/pdf')

    filename = 'guest_list.pdf'
    if selected_date:
        filename = f'guest_list_{selected_date}.pdf'

    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)

    return response


@login_required
def check_out_guest(request):
    bookings = Booking.objects.select_related('guest', 'room').filter(
        status='CHECKED_IN'
    ).order_by('-created_at')

    return render(request, 'reception/check_out_guest.html', {
        'bookings': bookings
    })


@login_required
def process_check_out(request, booking_id):
    booking = get_object_or_404(
        Booking.objects.select_related('guest', 'room'),
        id=booking_id
    )

    if booking.status == 'CHECKED_OUT':
        messages.error(request, 'This guest has already been checked out.')
        return redirect('reception:booking_detail', booking.id)

    charges = booking.charges.all().order_by('-created_at')

    accommodation_amount = booking.total_amount
    extra_charges_total = charges.aggregate(
        total=Sum('total_amount')
    )['total'] or 0

    grand_total = accommodation_amount + extra_charges_total
    total_paid = booking.amount_paid
    balance = grand_total - total_paid

    if request.method == 'POST':
        form = CheckOutForm(request.POST)

        if form.is_valid():
            final_payment = form.cleaned_data.get('final_payment') or 0
            payment_method = form.cleaned_data.get('payment_method')
            payment_reference = form.cleaned_data.get('payment_reference')
            room_condition_note = form.cleaned_data.get('room_condition_note')

            if final_payment > 0:
                Payment.objects.create(
                    booking=booking,
                    received_by=request.user,
                    amount=final_payment,
                    payment_method=payment_method,
                    reference=payment_reference,
                    note='Final payment made during checkout'
                )

                booking.amount_paid += final_payment

            checkout, created = CheckOut.objects.get_or_create(
                booking=booking,
                defaults={
                    'checked_out_by': request.user,
                    'note': room_condition_note
                }
            )

            if not created:
                messages.error(request, 'This guest has already been checked out.')
                return redirect('reception:booking_detail', booking.id)

            booking.status = 'CHECKED_OUT'
            booking.total_amount = grand_total
            booking.save()

            booking.room.status = 'DIRTY'
            booking.room.save()

            RoomCleaning.objects.get_or_create(
                room=booking.room,
                status='DIRTY',
                defaults={
                    'priority': 'MEDIUM',
                    'cleaning_note': f'Auto-generated after checkout of {booking.guest.full_name}'
                }
            )

            messages.success(request, 'Guest checked out successfully.')
            return redirect('reception:booking_detail', booking.id)

    else:
        form = CheckOutForm(initial={
            'final_payment': balance if balance > 0 else 0
        })

    return render(request, 'reception/process_check_out.html', {
        'booking': booking,
        'charges': charges,
        'form': form,
        'accommodation_amount': accommodation_amount,
        'extra_charges_total': extra_charges_total,
        'grand_total': grand_total,
        'total_paid': total_paid,
        'balance': balance,
    })


@login_required
def download_checkout_pdf(request, booking_id):
    booking = get_object_or_404(
        Booking.objects.select_related('guest', 'room'),
        id=booking_id
    )

    charges = booking.charges.all().order_by('created_at')
    payments = booking.payments.all().order_by('payment_date')

    extra_charges_total = charges.aggregate(total=Sum('total_amount'))['total'] or 0
    accommodation_amount = booking.total_amount - extra_charges_total
    grand_total = booking.total_amount
    total_paid = booking.amount_paid
    balance = grand_total - total_paid

    html = get_template('reception/checkout_pdf.html').render({
        'booking': booking,
        'charges': charges,
        'payments': payments,
        'accommodation_amount': accommodation_amount,
        'extra_charges_total': extra_charges_total,
        'grand_total': grand_total,
        'total_paid': total_paid,
        'balance': balance,
    })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="checkout_bill_{booking.guest.full_name}_{booking.id}.pdf"'
    )

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)

    return response


@login_required
def process_check_out(request, booking_id):
    booking = get_object_or_404(
        Booking.objects.select_related('guest', 'room'),
        id=booking_id
    )

    charges = booking.charges.all().order_by('-created_at')

    accommodation_amount = booking.total_amount
    extra_charges_total = charges.aggregate(
        total=Sum('total_amount')
    )['total'] or 0

    grand_total = accommodation_amount + extra_charges_total
    total_paid = booking.amount_paid
    balance = grand_total - total_paid

    if request.method == 'POST':
        form = CheckOutForm(request.POST)

        if form.is_valid():
            final_payment = form.cleaned_data.get('final_payment') or 0
            payment_method = form.cleaned_data.get('payment_method')
            payment_reference = form.cleaned_data.get('payment_reference')
            room_condition_note = form.cleaned_data.get('room_condition_note')

            if final_payment > 0:
                Payment.objects.create(
                    booking=booking,
                    received_by=request.user,
                    amount=final_payment,
                    payment_method=payment_method,
                    reference=payment_reference,
                    note='Final payment made during checkout'
                )

                booking.amount_paid += final_payment

            CheckOut.objects.create(
                booking=booking,
                checked_out_by=request.user,
                note=room_condition_note
            )

            booking.status = 'CHECKED_OUT'
            booking.total_amount = grand_total
            booking.save()

            booking.room.status = 'DIRTY'
            booking.room.save()

            messages.success(request, 'Guest checked out successfully.')
            return redirect('reception:booking_detail', booking.id)

    else:
        form = CheckOutForm(initial={
            'final_payment': balance if balance > 0 else 0
        })

    return render(request, 'reception/process_check_out.html', {
        'booking': booking,
        'charges': charges,
        'form': form,
        'accommodation_amount': accommodation_amount,
        'extra_charges_total': extra_charges_total,
        'grand_total': grand_total,
        'total_paid': total_paid,
        'balance': balance,
    })


@login_required
def download_checkout_pdf(request, booking_id):
    booking = get_object_or_404(
        Booking.objects.select_related('guest', 'room'),
        id=booking_id
    )

    charges = booking.charges.all().order_by('created_at')
    payments = booking.payments.all().order_by('payment_date')

    extra_charges_total = charges.aggregate(total=Sum('total_amount'))['total'] or 0
    accommodation_amount = booking.total_amount - extra_charges_total
    grand_total = booking.total_amount
    total_paid = booking.amount_paid
    balance = grand_total - total_paid

    html = get_template('reception/checkout_pdf.html').render({
        'booking': booking,
        'charges': charges,
        'payments': payments,
        'accommodation_amount': accommodation_amount,
        'extra_charges_total': extra_charges_total,
        'grand_total': grand_total,
        'total_paid': total_paid,
        'balance': balance,
    })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="checkout_bill_{booking.guest.full_name}_{booking.id}.pdf"'
    )

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)

    return response


@login_required
def daily_report(request):
    return render(request, 'reception/daily_report.html')

def get_finance_report_data(selected_date):
    payments = Payment.objects.select_related(
        'booking',
        'booking__guest',
        'booking__room',
        'received_by'
    ).filter(payment_date__date=selected_date)

    bookings = Booking.objects.select_related(
        'guest',
        'room',
        'booked_by'
    ).filter(created_at__date=selected_date)

    checkins = CheckIn.objects.select_related(
        'booking',
        'booking__guest',
        'booking__room',
        'checked_in_by'
    ).filter(check_in_time__date=selected_date)

    checkouts = CheckOut.objects.select_related(
        'booking',
        'booking__guest',
        'booking__room',
        'checked_out_by'
    ).filter(check_out_time__date=selected_date)

    charges = GuestCharge.objects.select_related(
        'booking',
        'booking__guest',
        'booking__room',
        'added_by'
    ).filter(created_at__date=selected_date)

    total_payments = payments.aggregate(total=Sum('amount'))['total'] or 0

    cash_total = payments.filter(payment_method='CASH').aggregate(total=Sum('amount'))['total'] or 0
    transfer_total = payments.filter(payment_method='TRANSFER').aggregate(total=Sum('amount'))['total'] or 0
    pos_total = payments.filter(payment_method='POS').aggregate(total=Sum('amount'))['total'] or 0
    card_total = payments.filter(payment_method='CARD').aggregate(total=Sum('amount'))['total'] or 0
    other_total = payments.filter(payment_method='OTHER').aggregate(total=Sum('amount'))['total'] or 0

    room_sales_total = bookings.aggregate(total=Sum('total_amount'))['total'] or 0
    service_charges_total = charges.aggregate(total=Sum('total_amount'))['total'] or 0

    outstanding_balance = 0
    for booking in bookings:
        outstanding_balance += booking.balance()

    return {
        'payments': payments,
        'bookings': bookings,
        'checkins': checkins,
        'checkouts': checkouts,
        'charges': charges,

        'total_payments': total_payments,
        'cash_total': cash_total,
        'transfer_total': transfer_total,
        'pos_total': pos_total,
        'card_total': card_total,
        'other_total': other_total,

        'room_sales_total': room_sales_total,
        'service_charges_total': service_charges_total,
        'outstanding_balance': outstanding_balance,

        'booking_count': bookings.count(),
        'checkin_count': checkins.count(),
        'checkout_count': checkouts.count(),
        'payment_count': payments.count(),
        'charge_count': charges.count(),
    }


@login_required
def finance_report(request):
    selected_date = request.GET.get('date')

    if selected_date:
        selected_date_obj = datetime.strptime(selected_date, '%Y-%m-%d').date()
    else:
        selected_date_obj = timezone.localdate()
        selected_date = selected_date_obj.strftime('%Y-%m-%d')

    report = get_finance_report_data(selected_date_obj)

    return render(request, 'reception/finance_report.html', {
        'selected_date': selected_date,
        'report': report,
    })

@login_required
def download_finance_report_pdf(request):
    selected_date = request.GET.get('date')

    if selected_date:
        selected_date_obj = datetime.strptime(selected_date, '%Y-%m-%d').date()
    else:
        selected_date_obj = timezone.localdate()
        selected_date = selected_date_obj.strftime('%Y-%m-%d')

    report = get_finance_report_data(selected_date_obj)
    generated_at = timezone.now()

    html = get_template('reception/finance_report_pdf.html').render({
        'selected_date': selected_date,
        'report': report,
        'generated_at': generated_at,
        'generated_by': request.user,
    })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="reception_financial_report_{selected_date}.pdf"'
    )

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Error generating financial report PDF', status=500)

    return response


@login_required
def room_service_list(request):
    services = RoomServiceRequest.objects.select_related(
        'booking',
        'booking__guest',
        'booking__room',
        'requested_by'
    ).order_by('-created_at')

    return render(request, 'reception/room_service_list.html', {
        'services': services
    })


@login_required
def create_room_service(request):
    if request.method == 'POST':
        form = RoomServiceRequestForm(request.POST)

        if form.is_valid():
            service = form.save(commit=False)
            service.requested_by = request.user
            service.save()

            messages.success(request, 'Room service request created successfully.')
            return redirect('reception:room_service_list')
    else:
        form = RoomServiceRequestForm()

    return render(request, 'reception/create_room_service.html', {
        'form': form
    })


@login_required
def complete_room_service(request, service_id):
    service = get_object_or_404(RoomServiceRequest, id=service_id)

    if service.status == 'COMPLETED':
        messages.error(request, 'This room service has already been completed.')
        return redirect('reception:room_service_list')

    service.status = 'COMPLETED'
    service.completed_at = timezone.now()

    if service.is_billable and not service.added_to_guest_bill:
        GuestCharge.objects.create(
            booking=service.booking,
            category='ROOM_SERVICE',
            item_name=service.request_title,
            quantity=service.quantity,
            unit_price=service.unit_price,
            total_amount=service.total_amount,
            added_by=request.user
        )

        service.added_to_guest_bill = True

    service.save()

    messages.success(request, 'Room service completed and added to guest bill.')
    return redirect('reception:room_service_list')


@login_required
def cancel_room_service(request, service_id):
    service = get_object_or_404(RoomServiceRequest, id=service_id)

    if service.status == 'COMPLETED':
        messages.error(request, 'Completed room service cannot be cancelled.')
        return redirect('reception:room_service_list')

    service.status = 'CANCELLED'
    service.save()

    messages.success(request, 'Room service request cancelled.')
    return redirect('reception:room_service_list')


@login_required
def reports_center(request):
    report_type = request.GET.get('report_type', 'in_house')
    selected_date = request.GET.get('date')

    if selected_date:
        selected_date_obj = datetime.strptime(selected_date, '%Y-%m-%d').date()
    else:
        selected_date_obj = timezone.localdate()
        selected_date = selected_date_obj.strftime('%Y-%m-%d')

    context = build_reception_report(report_type, selected_date_obj)

    return render(request, 'reception/reports_center.html', {
        'report_type': report_type,
        'selected_date': selected_date,
        **context
    })


def build_reception_report(report_type, selected_date):
    if report_type == 'in_house':
        bookings = Booking.objects.select_related('guest', 'room').filter(
            status='CHECKED_IN'
        )

        return {
            'title': 'In-House Guest Report',
            'bookings': bookings,
            'total_count': bookings.count(),
        }

    elif report_type == 'occupancy':
        rooms = Room.objects.all()

        total_rooms = rooms.count()
        occupied = rooms.filter(status='OCCUPIED').count()
        available = rooms.filter(status='AVAILABLE').count()
        reserved = rooms.filter(status='RESERVED').count()
        dirty = rooms.filter(status='DIRTY').count()
        maintenance = rooms.filter(status='MAINTENANCE').count()

        occupancy_rate = 0
        if total_rooms > 0:
            occupancy_rate = round((occupied / total_rooms) * 100, 2)

        return {
            'title': 'Occupancy Report',
            'rooms': rooms,
            'total_rooms': total_rooms,
            'occupied': occupied,
            'available': available,
            'reserved': reserved,
            'dirty': dirty,
            'maintenance': maintenance,
            'occupancy_rate': occupancy_rate,
        }

    elif report_type == 'arrivals':
        bookings = Booking.objects.select_related('guest', 'room').filter(
            check_in_date=selected_date
        )

        return {
            'title': 'Guest Arrival Report',
            'bookings': bookings,
            'total_count': bookings.count(),
        }

    elif report_type == 'departures':
        bookings = Booking.objects.select_related('guest', 'room').filter(
            check_out_date=selected_date
        )

        return {
            'title': 'Guest Departure Report',
            'bookings': bookings,
            'total_count': bookings.count(),
        }

    elif report_type == 'outstanding':
        bookings = Booking.objects.select_related('guest', 'room').exclude(
            status='CANCELLED'
        )

        outstanding_bookings = []
        total_outstanding = 0

        for booking in bookings:
            balance = booking.balance()
            if balance > 0:
                outstanding_bookings.append(booking)
                total_outstanding += balance

        return {
            'title': 'Outstanding Balance Report',
            'bookings': outstanding_bookings,
            'total_outstanding': total_outstanding,
            'total_count': len(outstanding_bookings),
        }

    elif report_type == 'room_service':
        services = RoomServiceRequest.objects.select_related(
            'booking',
            'booking__guest',
            'booking__room'
        ).filter(created_at__date=selected_date)

        total_amount = services.aggregate(total=Sum('total_amount'))['total'] or 0

        return {
            'title': 'Room Service Report',
            'services': services,
            'total_amount': total_amount,
            'total_count': services.count(),
        }

    else:
        return {
            'title': 'Invalid Report',
        }


@login_required
def download_reception_report_pdf(request):
    report_type = request.GET.get('report_type', 'in_house')
    selected_date = request.GET.get('date')

    if selected_date:
        selected_date_obj = datetime.strptime(selected_date, '%Y-%m-%d').date()
    else:
        selected_date_obj = timezone.localdate()
        selected_date = selected_date_obj.strftime('%Y-%m-%d')

    context = build_reception_report(report_type, selected_date_obj)

    html = get_template('reception/reception_report_pdf.html').render({
        'report_type': report_type,
        'selected_date': selected_date,
        'generated_at': timezone.now(),
        'generated_by': request.user,
        **context
    })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="{report_type}_report_{selected_date}.pdf"'
    )

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Error generating report PDF', status=500)

    return response