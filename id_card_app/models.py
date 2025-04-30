from django.db import models

# Create your models here.

class Student(models.Model):
    name = models.CharField(max_length=100)
    father_name = models.CharField(max_length=100)
    mother_name = models.CharField(max_length=100)
    student_class = models.CharField(max_length=10)
    section = models.CharField(max_length=10)
    roll_no = models.CharField(max_length=10)
    address = models.TextField()
    mobile = models.CharField(max_length=15)
    image = models.ImageField(upload_to='cards/', null=True, blank=True)

    def __str__(self):
        return self.name