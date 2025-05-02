from django import forms
from .models import Student

class StudentForm(forms.ModelForm):
    # Define choices for dropdown selections
    CLASS_CHOICES = [
        ('Nursery', 'Nursery'),
        ('UKG', 'UKG'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ('6', '6'),
        ('7', '7'),
        ('8', '8'),
    ]
    
    SECTION_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
    ]
    
    # Override the fields to use select dropdown widgets with required=True
    student_class = forms.ChoiceField(
        choices=CLASS_CHOICES, 
        widget=forms.Select(attrs={'class': 'form-control', 'required': True}),
        required=True
    )
    section = forms.ChoiceField(
        choices=SECTION_CHOICES, 
        widget=forms.Select(attrs={'class': 'form-control', 'required': True}),
        required=True
    )
    
    class Meta:
        model = Student
        exclude = ['image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter student name', 'required': True}),
            'father_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter father name', 'required': True}),
            'mother_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter mother name', 'required': True}),
            'roll_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter roll number', 'required': True}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter address', 'rows': 3, 'required': True}),
            'mobile': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter mobile number', 'required': True}),
            'profile_photo': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super(StudentForm, self).__init__(*args, **kwargs)
        # Set all fields as required except profile_photo
        for field_name, field in self.fields.items():
            if field_name != 'profile_photo':  # Make profile_photo optional
                field.required = True
