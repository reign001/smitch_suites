from django.shortcuts import render

# Create your views here.
from datetime import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa

from .models import VisitorLog, SecurityIncident, BlacklistRecord, KeyCardLog, PatrolLog
from .forms import (
    VisitorLogForm,
    SecurityIncidentForm,
    BlacklistRecordForm,
    KeyCardLogForm,
    PatrolLogForm,
)


@login_required
def security_dashboard(request):
    today = timezone.localdate()

    return render(request, 'security/dashboard.html', {
        'visitors_today': VisitorLog.objects.filter(entry_time__date=today).count(),
        'active_visitors': VisitorLog.objects.filter(exit_time__isnull=True).count(),
        'incidents_today': SecurityIncident.objects.filter(incident_time__date=today).count(),
        'blacklisted_count': BlacklistRecord.objects.count(),
        'patrols_today': PatrolLog.objects.filter(patrol_time__date=today).count(),
    })


@login_required
def visitor_list(request):
    visitors = VisitorLog.objects.select_related('checked_in_by').order_by('-entry_time')
    return render(request, 'security/visitor_list.html', {'visitors': visitors})


@login_required
def create_visitor_log(request):
    if request.method == 'POST':
        form = VisitorLogForm(request.POST)

        if form.is_valid():
            visitor = form.save(commit=False)
            visitor.checked_in_by = request.user
            visitor.save()
            messages.success(request, 'Visitor logged successfully.')
            return redirect('security:visitor_list')
    else:
        form = VisitorLogForm()

    return render(request, 'security/create_visitor_log.html', {'form': form})


@login_required
def checkout_visitor(request, visitor_id):
    visitor = get_object_or_404(VisitorLog, id=visitor_id)

    if visitor.exit_time:
        messages.error(request, 'This visitor has already checked out.')
    else:
        visitor.exit_time = timezone.now()
        visitor.save()
        messages.success(request, 'Visitor checked out successfully.')

    return redirect('security:visitor_list')


@login_required
def incident_list(request):
    incidents = SecurityIncident.objects.select_related('guest', 'room', 'reported_by').order_by('-incident_time')
    return render(request, 'security/incident_list.html', {'incidents': incidents})


@login_required
def create_incident(request):
    if request.method == 'POST':
        form = SecurityIncidentForm(request.POST)

        if form.is_valid():
            incident = form.save(commit=False)
            incident.reported_by = request.user
            incident.save()
            messages.success(request, 'Security incident recorded successfully.')
            return redirect('security:incident_list')
    else:
        form = SecurityIncidentForm()

    return render(request, 'security/create_incident.html', {'form': form})


@login_required
def blacklist_list(request):
    records = BlacklistRecord.objects.select_related('added_by').order_by('-date_added')
    return render(request, 'security/blacklist_list.html', {'records': records})


@login_required
def create_blacklist_record(request):
    if request.method == 'POST':
        form = BlacklistRecordForm(request.POST)

        if form.is_valid():
            record = form.save(commit=False)
            record.added_by = request.user
            record.save()
            messages.success(request, 'Blacklist record added successfully.')
            return redirect('security:blacklist_list')
    else:
        form = BlacklistRecordForm()

    return render(request, 'security/create_blacklist_record.html', {'form': form})


@login_required
def keycard_list(request):
    logs = KeyCardLog.objects.select_related('room', 'guest', 'handled_by').order_by('-created_at')
    return render(request, 'security/keycard_list.html', {'logs': logs})


@login_required
def create_keycard_log(request):
    if request.method == 'POST':
        form = KeyCardLogForm(request.POST)

        if form.is_valid():
            log = form.save(commit=False)
            log.handled_by = request.user
            log.save()
            messages.success(request, 'Key/card record saved successfully.')
            return redirect('security:keycard_list')
    else:
        form = KeyCardLogForm()

    return render(request, 'security/create_keycard_log.html', {'form': form})


@login_required
def patrol_list(request):
    patrols = PatrolLog.objects.select_related('officer').order_by('-patrol_time')
    return render(request, 'security/patrol_list.html', {'patrols': patrols})


@login_required
def create_patrol_log(request):
    if request.method == 'POST':
        form = PatrolLogForm(request.POST)

        if form.is_valid():
            patrol = form.save(commit=False)
            patrol.officer = request.user
            patrol.save()
            messages.success(request, 'Patrol log saved successfully.')
            return redirect('security:patrol_list')
    else:
        form = PatrolLogForm()

    return render(request, 'security/create_patrol_log.html', {'form': form})


@login_required
def security_report(request):
    selected_date = request.GET.get('date')

    if selected_date:
        report_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
    else:
        report_date = timezone.localdate()
        selected_date = report_date.strftime('%Y-%m-%d')

    visitors = VisitorLog.objects.filter(entry_time__date=report_date)
    incidents = SecurityIncident.objects.filter(incident_time__date=report_date)
    patrols = PatrolLog.objects.filter(patrol_time__date=report_date)
    key_logs = KeyCardLog.objects.filter(created_at__date=report_date)

    return render(request, 'security/security_report.html', {
        'selected_date': selected_date,
        'visitors': visitors,
        'incidents': incidents,
        'patrols': patrols,
        'key_logs': key_logs,
    })


@login_required
def download_security_report_pdf(request):
    selected_date = request.GET.get('date')

    if selected_date:
        report_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
    else:
        report_date = timezone.localdate()
        selected_date = report_date.strftime('%Y-%m-%d')

    visitors = VisitorLog.objects.filter(entry_time__date=report_date)
    incidents = SecurityIncident.objects.filter(incident_time__date=report_date)
    patrols = PatrolLog.objects.filter(patrol_time__date=report_date)
    key_logs = KeyCardLog.objects.filter(created_at__date=report_date)

    html = get_template('security/security_report_pdf.html').render({
        'selected_date': selected_date,
        'generated_at': timezone.now(),
        'generated_by': request.user,
        'visitors': visitors,
        'incidents': incidents,
        'patrols': patrols,
        'key_logs': key_logs,
    })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="security_report_{selected_date}.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Error generating security report PDF', status=500)

    return response