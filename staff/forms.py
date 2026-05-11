from django import forms
from accounts.models import CustomUser
from .models import StaffProfile


class StaffCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    department = forms.ChoiceField(choices=StaffProfile.DEPARTMENT_CHOICES)
    job_title = forms.CharField(max_length=150)
    salary = forms.DecimalField(max_digits=12, decimal_places=2)
    employment_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    address = forms.CharField(widget=forms.Textarea, required=False)
    next_of_kin = forms.CharField(max_length=200, required=False)
    next_of_kin_phone = forms.CharField(max_length=20, required=False)

    class Meta:
        model = CustomUser
        fields = ['username', 'full_name', 'phone', 'email', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])

        if commit:
            user.save()

            StaffProfile.objects.create(
                user=user,
                department=self.cleaned_data['department'],
                job_title=self.cleaned_data['job_title'],
                salary=self.cleaned_data['salary'],
                employment_date=self.cleaned_data['employment_date'],
                phone=self.cleaned_data['phone'],
                address=self.cleaned_data['address'],
                next_of_kin=self.cleaned_data['next_of_kin'],
                next_of_kin_phone=self.cleaned_data['next_of_kin_phone'],
            )

        return user