from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import StaffProfile
from .forms import StaffCreationForm


@login_required
def staff_list(request):
    staff_members = StaffProfile.objects.select_related('user').all()
    return render(request, 'staff/staff_list.html', {
        'staff_members': staff_members
    })


@login_required
def add_staff(request):
    if request.method == 'POST':
        form = StaffCreationForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('staff:staff_list')
    else:
        form = StaffCreationForm()

    return render(request, 'staff/add_staff.html', {
        'form': form
    })