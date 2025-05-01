from django.shortcuts import render, redirect, get_object_or_404
from .forms import StudentForm
from .models import Student
from PIL import Image, ImageDraw, ImageFont
from django.http import FileResponse, HttpResponse
import os
from django.conf import settings
import traceback

def home(request):
    return render(request, 'id_card_app/index.html')

def new_id_card(request):
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                student = form.save(commit=False)
                
                # Handle profile photo upload
                if 'profile_photo' in request.FILES:
                    student.profile_photo = request.FILES['profile_photo']
                
                # Save student first to ensure profile_photo is saved
                student.save()

                # Get the template image path
                template_path = os.path.join(settings.BASE_DIR, 'id_card_app', 'static', 'zza_idcardTemplate.png')
                
                # Load template correctly
                template = Image.open(template_path).convert("RGBA")
                draw = ImageDraw.Draw(template)

                # Get the font with correct path
                font_path = os.path.join(settings.BASE_DIR, 'id_card_app', 'static', 'fonts', 'Poppins-Regular.ttf')
                font = ImageFont.truetype(font_path, 20)

                # Draw text with student data from form
                draw.text((50, 5), f"Name: {student.name}", font=font, fill="black")
                draw.text((50, 100), f"Father: {student.father_name}", font=font, fill="black")
                draw.text((50, 140), f"Mother: {student.mother_name}", font=font, fill="black")
                draw.text((50, 180), f"Class: {student.student_class}", font=font, fill="black")
                draw.text((50, 220), f"Section: {student.section}", font=font, fill="black")
                draw.text((50, 260), f"Roll No: {student.roll_no}", font=font, fill="black")
                draw.text((50, 300), f"Mobile: {student.mobile}", font=font, fill="black")

                # Add profile photo to ID card if available
                if student.profile_photo:
                    # Position for profile photo (adjust as needed)
                    photo_position = (400, 80)  # Right side of card
                    photo_size = (150, 150)    # Size of photo on card
                    
                    # Open and resize profile photo
                    profile_photo_path = os.path.join(settings.MEDIA_ROOT, student.profile_photo.name)
                    if os.path.exists(profile_photo_path):
                        photo = Image.open(profile_photo_path).convert("RGBA")
                        photo = photo.resize(photo_size)
                        
                        # Paste photo onto template
                        template.paste(photo, photo_position, photo)

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
            except Exception as e:
                # Print error for debugging
                print(f"Error generating ID card: {str(e)}")
                print(traceback.format_exc())
                # Create an error message to display to user
                form.add_error(None, f"Error generating ID card: {str(e)}")
    else:
        form = StudentForm()
    return render(request, 'id_card_app/form.html', {'form': form})

def view_all(request):
    students = Student.objects.all()
    return render(request, 'id_card_app/view_all.html', {'students': students})

def edit_id_card(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            try:
                student = form.save(commit=False)
                
                # Handle profile photo upload if a new one is provided
                if 'profile_photo' in request.FILES:
                    # If there's an existing photo, optionally delete it
                    if student.profile_photo:
                        old_photo_path = os.path.join(settings.MEDIA_ROOT, student.profile_photo.name)
                        if os.path.exists(old_photo_path) and os.path.basename(old_photo_path) != os.path.basename(request.FILES['profile_photo'].name):
                            try:
                                os.remove(old_photo_path)
                            except:
                                pass
                    
                    student.profile_photo = request.FILES['profile_photo']
                
                # Save student first to ensure profile_photo is saved if updated
                student.save()
                
                # Regenerate the ID card image
                template_path = os.path.join(settings.BASE_DIR, 'id_card_app', 'static', 'zza_idcardTemplate.png')
                template = Image.open(template_path).convert("RGBA")
                draw = ImageDraw.Draw(template)

                font_path = os.path.join(settings.BASE_DIR, 'id_card_app', 'static', 'fonts', 'Poppins-Regular.ttf')
                font = ImageFont.truetype(font_path, 20)

                # Draw text on the template with student data
                draw.text((222, 400), f"{student.name}", font=font, fill="#0071BC")
                draw.text((50, 100), f"{student.father_name}", font=font, fill="black")
                draw.text((50, 140), f"{student.mother_name}", font=font, fill="black")
                draw.text((50, 180), f"{student.student_class}", font=font, fill="black")
                draw.text((50, 220), f"{student.section}", font=font, fill="black")
                draw.text((50, 260), f"{student.roll_no}", font=font, fill="black")
                draw.text((50, 300), f"{student.mobile}", font=font, fill="black")

                # Add profile photo to ID card if available
                if student.profile_photo:
                    # Position for profile photo (adjust as needed)
                    photo_position = (185, 280)  # center side of card
                    photo_size = (225, 225)    # Size of photo on card
                    
                    # Open and resize profile photo
                    profile_photo_path = os.path.join(settings.MEDIA_ROOT, student.profile_photo.name)
                    if os.path.exists(profile_photo_path):
                        photo = Image.open(profile_photo_path).convert("RGBA")
                        photo = photo.resize(photo_size)
                        
                        # Paste photo onto template
                        template.paste(photo, photo_position, photo)

                # Save the updated ID card
                filename = f"{student.name}_{student.roll_no}.png"
                save_path = os.path.join(settings.MEDIA_ROOT, 'cards', filename)
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                template.save(save_path)

                student.image = f"cards/{filename}"
                student.save()
                return redirect('view_all')
            except Exception as e:
                # Print error for debugging
                print(f"Error updating ID card: {str(e)}")
                print(traceback.format_exc())
                # Create an error message to display to user
                form.add_error(None, f"Error updating ID card: {str(e)}")
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
