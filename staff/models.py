from django.db import models

# Create your models here.
from django.db import models

# Create your models here.
from django.db import models
from accounts.models import CustomUser


class StaffProfile(models.Model):
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('SUSPENDED', 'Suspended'),
        ('RESIGNED', 'Resigned'),
        ('TERMINATED', 'Terminated'),
    ]

    DEPARTMENT_CHOICES = [
        ('RECEPTION', 'Reception'),
        ('HOUSEKEEPING', 'Housekeeping'),
        ('RESTAURANT', 'Restaurant'),
        ('BAR', 'Bar'),
        ('HOUSEKEEPING', 'Housekeeping'),
        ('FINANCE', 'Finance'),
        ('SECURITY', 'Security'),
        ('STORE', 'Store'),
        ('OTHER', 'Other'),
        
    ]

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='staff_profile')
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES)
    job_title = models.CharField(max_length=150)
    salary = models.DecimalField(max_digits=12, decimal_places=2)
    employment_date = models.DateField()
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    next_of_kin = models.CharField(max_length=200, blank=True)
    next_of_kin_phone = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.full_name} - {self.job_title}"


class Attendance(models.Model):
    STATUS_CHOICES = [
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
        ('LATE', 'Late'),
        ('HALF_DAY', 'Half Day'),
    ]

    staff = models.ForeignKey(StaffProfile, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    clock_in = models.TimeField(blank=True, null=True)
    clock_out = models.TimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PRESENT')
    note = models.TextField(blank=True)

    class Meta:
        unique_together = ('staff', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.staff.user.full_name} - {self.date}"