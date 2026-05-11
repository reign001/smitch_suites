from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum

from reception.models import Room, Booking, Payment
from restaurant.models import RestaurantOrder
from bar.models import BarSale
from housekeeping.models import LaundryRequest


@login_required
def admin_dashboard(request):
    today = timezone.localdate()

    total_rooms = Room.objects.count()

    current_guests = Booking.objects.filter(
        status='CHECKED_IN'
    ).count()

    todays_bookings = Booking.objects.filter(
        created_at__date=today
    ).count()

    accommodation_revenue = Payment.objects.filter(
        payment_date__date=today
    ).aggregate(total=Sum('amount'))['total'] or 0

    restaurant_revenue = RestaurantOrder.objects.filter(
        created_at__date=today
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    bar_revenue = BarSale.objects.filter(
        created_at__date=today
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    laundry_revenue = LaundryRequest.objects.filter(
        delivered_at__date=today
    ).aggregate(total=Sum('amount'))['total'] or 0

    todays_revenue = (
        accommodation_revenue +
        restaurant_revenue +
        bar_revenue +
        laundry_revenue
    )

    context = {
        'total_rooms': total_rooms,
        'current_guests': current_guests,
        'todays_bookings': todays_bookings,
        'todays_revenue': todays_revenue,
    }

    return render(request, 'dashboard/admin_dashboard.html', context)