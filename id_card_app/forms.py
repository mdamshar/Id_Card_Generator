from django import forms
from .models import Student

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        exclude = ['image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter student name'}),
            'father_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter father name'}),
            'mother_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter mother name'}),
            'student_class': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter class (e.g., 10)'}),
            'section': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter section (e.g., A)'}),
            'roll_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter roll number'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter address', 'rows': 3}),
            'mobile': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter mobile number'}),
            'profile_photo': forms.FileInput(attrs={'class': 'form-control'}),
        }
