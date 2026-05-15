from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import VisitorLog, SecurityIncident, BlacklistRecord, KeyCardLog, PatrolLog

admin.site.register(VisitorLog)
admin.site.register(SecurityIncident)
admin.site.register(BlacklistRecord)
admin.site.register(KeyCardLog)
admin.site.register(PatrolLog)