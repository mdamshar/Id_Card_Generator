from django.shortcuts import render, redirect, get_object_or_404
from .forms import StudentForm
from .models import Student
from PIL import Image, ImageDraw, ImageFont
from django.http import FileResponse, HttpResponse
import os
from django.conf import settings

def home(request):
    return render(request, 'id_card_app/index.html')

def new_id_card(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save(commit=False)

            # Get the template image path
            template_path = os.path.join(settings.BASE_DIR, 'id_card_app/static/zza_idcardTemplate.png')
            
            # Load template correctly
            template = Image.open(template_path).convert("RGBA")
            draw = ImageDraw.Draw(template)

            # Get the font
            font_path = os.path.join(settings.BASE_DIR, 'id_card_app/static/fonts/Poppins-Regular.ttf')
            font = ImageFont.truetype(font_path, 20)

            # Draw text with student data from form
            draw.text((50, 60), f"Name: {student.name}", font=font, fill="black")
            draw.text((50, 100), f"Father: {student.father_name}", font=font, fill="black")
            draw.text((50, 140), f"Mother: {student.mother_name}", font=font, fill="black")
            draw.text((50, 180), f"Class: {student.student_class}", font=font, fill="black")
            draw.text((50, 220), f"Section: {student.section}", font=font, fill="black")
            draw.text((50, 260), f"Roll No: {student.roll_no}", font=font, fill="black")
            draw.text((50, 300), f"Mobile: {student.mobile}", font=font, fill="black")

            # Create filename and save path
            filename = f"{student.name}_{student.roll_no}.png"
            save_path = os.path.join(settings.MEDIA_ROOT, 'cards', filename)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            # Save the generated ID card
            template.save(save_path)

            # Update student record with image path
            student.image = f"cards/{filename}"
            student.save()
            return redirect('view_all')
    else:
        form = StudentForm()
    return render(request, 'id_card_app/form.html', {'form': form})

def view_all(request):
    students = Student.objects.all()
    return render(request, 'id_card_app/view_all.html', {'students': students})

def edit_id_card(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            student = form.save(commit=False)
            
            # Regenerate the ID card image
            template_path = os.path.join(settings.BASE_DIR, 'id_card_app/static/zza_idcardTemplate.png')
            template = Image.open(template_path).convert("RGBA")
            draw = ImageDraw.Draw(template)

            font_path = os.path.join(settings.BASE_DIR, 'id_card_app/static/fonts/Poppins-Regular.ttf')
            font = ImageFont.truetype(font_path, 20)

            # Draw text on the template with student data
            draw.text((50, 60), f"Name: {student.name}", font=font, fill="black")
            draw.text((50, 100), f"Father: {student.father_name}", font=font, fill="black")
            draw.text((50, 140), f"Mother: {student.mother_name}", font=font, fill="black")
            draw.text((50, 180), f"Class: {student.student_class}", font=font, fill="black")
            draw.text((50, 220), f"Section: {student.section}", font=font, fill="black")
            draw.text((50, 260), f"Roll No: {student.roll_no}", font=font, fill="black")
            draw.text((50, 300), f"Mobile: {student.mobile}", font=font, fill="black")

            # Save the updated ID card
            filename = f"{student.name}_{student.roll_no}.png"
            save_path = os.path.join(settings.MEDIA_ROOT, 'cards', filename)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            template.save(save_path)

            student.image = f"cards/{filename}"
            student.save()
            return redirect('view_all')
    else:
        form = StudentForm(instance=student)
    
    return render(request, 'id_card_app/form.html', {'form': form, 'edit_mode': True})

def delete_id_card(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    
    if request.method == 'POST':
        # Delete the associated image file if it exists
        if student.image:
            image_path = os.path.join(settings.MEDIA_ROOT, student.image.name)
            if os.path.exists(image_path):
                os.remove(image_path)
        
        # Delete the student record
        student.delete()
        return redirect('view_all')
    
    return render(request, 'id_card_app/confirm_delete.html', {'student': student})

def download_id_card(request):
    file_path = os.path.join('media', 'id_cards', 'generated_card.png')  # Adjust path
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename='id_card.png')
    else:
        return HttpResponse("ID Card not found.")
    
def submit_form(request):
    if request.method == 'POST':
        # Save student data + generate ID card image
        # Example: save_data_and_generate_card()

        # Redirect to download
        return redirect('download_id_card')
