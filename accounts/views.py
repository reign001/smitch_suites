from django.shortcuts import render

# Create your views here.
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages


def staff_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if user.is_superuser:
                return redirect('dashboard:admin_dashboard')

            try:
                staff_profile = user.staff_profile
            except Exception as e:
                messages.error(request, 'No staff profile found for this user.')
                return redirect('landing')

            if staff_profile.status != 'ACTIVE':
                messages.error(request, 'Your account is not active. Contact management.')
                return redirect('landing')

            elif staff_profile.department == 'RECEPTION':
                return redirect('reception:dashboard')

            elif staff_profile.department == 'MANAGEMENT':
                return redirect('dashboard:admin_dashboard')

            elif staff_profile.department == 'STORE':
                return redirect('inventory:dashboard')
            
            elif staff_profile.department == 'RESTAURANT':
                return redirect('restaurant:dashboard')
            
            elif staff_profile.department == 'BAR':
                return redirect('bar:dashboard')
            
            elif staff_profile.department == 'HOUSEKEEPING':
                return redirect('housekeeping:dashboard')
            
            elif staff_profile.department == 'FINANCE':
                    return redirect('finances:dashboard')
            
            elif staff_profile.department == 'SECURITY':
                    return redirect('security:dashboard')

            messages.error(request, 'No dashboard has been assigned to your department yet.')
            return redirect('landing')

        messages.error(request, 'Invalid username or password.')
        return redirect('landing')

    return redirect('landing')