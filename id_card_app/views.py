from django.shortcuts import render, redirect, get_object_or_404
from .forms import StudentForm
from .models import Student
from PIL import Image, ImageDraw, ImageFont
from django.http import FileResponse, HttpResponse, JsonResponse
import os
from django.conf import settings
import traceback
import io

# Import rembg for background removal with a fallback if not installed
try:
    from rembg import remove
    REMBG_AVAILABLE = True
except ImportError:
    REMBG_AVAILABLE = False

def home(request):
    return render(request, 'id_card_app/index.html')

def check_student_exists(request):
    """AJAX endpoint to check if a student with the given roll number already exists"""
    if request.method == 'POST':
        roll_no = request.POST.get('roll_no', '')
        existing_student = Student.objects.filter(roll_no=roll_no).first()
        if existing_student:
            return JsonResponse({
                'exists': True,
                'student_name': existing_student.name,
                'student_class': existing_student.student_class
            })
        return JsonResponse({'exists': False})
    return JsonResponse({'error': 'Invalid request method'})

def new_id_card(request):
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Check for existing student with the same roll number
                roll_no = form.cleaned_data.get('roll_no')
                override_existing = request.POST.get('override_existing', '') == 'true'
                
                existing_student = Student.objects.filter(roll_no=roll_no).first()
                if existing_student and not override_existing:
                    # If client-side validation is bypassed, still handle on server side
                    # The presence of override_existing=true means user confirmed the overwrite
                    form.add_error('roll_no', f"A student with roll number {roll_no} already exists")
                    return render(request, 'id_card_app/form.html', {'form': form})
                
                # If we're overriding an existing student, delete the old record
                if existing_student and override_existing:
                    # Delete the associated image file if it exists
                    if existing_student.image:
                        image_path = os.path.join(settings.MEDIA_ROOT, existing_student.image.name)
                        if os.path.exists(image_path):
                            os.remove(image_path)
                    existing_student.delete()
                
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

                # Draw text with student data from form - using consistent positioning with edit_id_card
                draw.text((222, 40), f"{student.name}", font=font, fill="#0071BC")
                draw.text((50, 100), f"{student.father_name}", font=font, fill="black")
                draw.text((50, 140), f"{student.mother_name}", font=font, fill="black")
                draw.text((50, 180), f"{student.student_class}", font=font, fill="black")
                draw.text((50, 220), f"{student.section}", font=font, fill="black")
                draw.text((50, 260), f"{student.roll_no}", font=font, fill="black")
                draw.text((50, 300), f"{student.mobile}", font=font, fill="black")

                # Add profile photo to ID card if available
                if student.profile_photo:
                    # Position for profile photo - matching edit_id_card function
                    photo_position = (250, 120)  # Centered in right portion of card
                    photo_size = (175, 175)      # Adjusted size for better fit
                    
                    # Open and resize profile photo
                    profile_photo_path = os.path.join(settings.MEDIA_ROOT, student.profile_photo.name)
                    if os.path.exists(profile_photo_path):
                        try:
                            # Try to remove background if rembg is available
                            if REMBG_AVAILABLE:
                                print(f"Using rembg to process photo for student: {student.name}")
                                with open(profile_photo_path, "rb") as photo_file:
                                    input_photo = photo_file.read()
                                    # Remove background from the image
                                    output_photo = remove(input_photo)
                                    photo = Image.open(io.BytesIO(output_photo)).convert("RGBA")
                                    photo = photo.resize(photo_size)
                                    
                                    # Paste photo onto template
                                    template.paste(photo, photo_position, photo)
                            else:
                                print(f"rembg not available, using standard method for student: {student.name}")
                                # Fallback if rembg is not available
                                photo = Image.open(profile_photo_path).convert("RGBA")
                                photo = photo.resize(photo_size)
                                template.paste(photo, photo_position, photo)
                        except Exception as e:
                            print(f"Error processing photo in new_id_card: {str(e)}")
                            print(f"Photo path: {profile_photo_path}")
                            print(f"REMBG_AVAILABLE: {REMBG_AVAILABLE}")
                            print(f"Photo position: {photo_position}, Photo size: {photo_size}")
                            print(traceback.format_exc())
                            # Fallback to standard method
                            photo = Image.open(profile_photo_path).convert("RGBA")
                            photo = photo.resize(photo_size)
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
    # Get all unique classes for the filter dropdown
    all_classes = Student.objects.values_list('student_class', flat=True).distinct().order_by('student_class')
    
    # Get the selected class filter from request
    selected_class = request.GET.get('class_filter', '')
    
    # Filter students based on the selected class
    if selected_class:
        students = Student.objects.filter(student_class=selected_class).order_by('name')
    else:
        students = Student.objects.all().order_by('name')
    
    context = {
        'students': students,
        'all_classes': all_classes,
        'selected_class': selected_class
    }
    return render(request, 'id_card_app/view_all.html', context)

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
                draw.text((222, 40), f"{student.name}", font=font, fill="#0071BC")
                draw.text((50, 100), f"{student.father_name}", font=font, fill="black")
                draw.text((50, 140), f"{student.mother_name}", font=font, fill="black")
                draw.text((50, 180), f"{student.student_class}", font=font, fill="black")
                draw.text((50, 220), f"{student.section}", font=font, fill="black")
                draw.text((50, 260), f"{student.roll_no}", font=font, fill="black")
                draw.text((50, 300), f"{student.mobile}", font=font, fill="black")

                # Add profile photo to ID card if available
                if student.profile_photo:
                    # Better position for profile photo
                    photo_position = (250, 120)  # Centered in right portion of card
                    photo_size = (175, 175)      # Adjusted size for better fit
                    
                    # Open and resize profile photo
                    profile_photo_path = os.path.join(settings.MEDIA_ROOT, student.profile_photo.name)
                    if os.path.exists(profile_photo_path):
                        try:
                            # Try to remove background if rembg is available
                            if REMBG_AVAILABLE:
                                print(f"Using rembg to process photo for student: {student.name}")
                                with open(profile_photo_path, "rb") as photo_file:
                                    input_photo = photo_file.read()
                                    # Remove background from the image
                                    output_photo = remove(input_photo)
                                    photo = Image.open(io.BytesIO(output_photo)).convert("RGBA")
                                    photo = photo.resize(photo_size)
                                    
                                    # Paste photo onto template
                                    template.paste(photo, photo_position, photo)
                            else:
                                print(f"rembg not available, using standard method for student: {student.name}")
                                # Fallback if rembg is not available
                                photo = Image.open(profile_photo_path).convert("RGBA")
                                photo = photo.resize(photo_size)
                                template.paste(photo, photo_position, photo)
                        except Exception as e:
                            print(f"Error processing photo in edit_id_card: {str(e)}")
                            print(f"Photo path: {profile_photo_path}")
                            print(f"REMBG_AVAILABLE: {REMBG_AVAILABLE}")
                            print(f"Photo position: {photo_position}, Photo size: {photo_size}")
                            print(traceback.format_exc())
                            # Fallback to standard method
                            photo = Image.open(profile_photo_path).convert("RGBA")
                            photo = photo.resize(photo_size)
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

def download_all_cards(request):
    import zipfile
    import io
    from django.http import FileResponse
    from django.utils import timezone
    
    # Get filter parameters
    selected_class = request.GET.get('class_filter', '')
    
    # Filter students based on the class (if specified)
    if selected_class:
        students = Student.objects.filter(student_class=selected_class).order_by('name')
        zip_filename = f"ID_Cards_{selected_class}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.zip"
    else:
        students = Student.objects.all().order_by('name')
        zip_filename = f"All_ID_Cards_{timezone.now().strftime('%Y%m%d_%H%M%S')}.zip"
    
    # Create a ZIP file in memory
    zip_buffer = io.BytesIO()
    
    # Count available images
    valid_images = 0
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for student in students:
            if student.image:
                image_path = os.path.join(settings.MEDIA_ROOT, student.image.name)
                if os.path.exists(image_path):
                    # Add the file to the ZIP with a descriptive filename
                    filename = f"{student.student_class}-{student.name}_{student.roll_no}.png"
                    zip_file.write(image_path, filename)
                    valid_images += 1
    
    # No images found
    if valid_images == 0:
        return HttpResponse("No ID card images available to download.")
    
    # Reset buffer position
    zip_buffer.seek(0)
    
    # Return the ZIP file as a response
    response = FileResponse(zip_buffer, as_attachment=True, filename=zip_filename)
    return response

def delete_all_cards(request):
    # Only process POST requests for security
    if request.method != 'POST':
        return redirect('view_all')
    
    # Get filter parameters
    selected_class = request.POST.get('class_filter', '')
    
    # Filter students based on the class (if specified)
    if selected_class:
        students = Student.objects.filter(student_class=selected_class)
    else:
        students = Student.objects.all()
    
    # Delete each student and their image
    deleted_count = 0
    for student in students:
        if student.image:
            image_path = os.path.join(settings.MEDIA_ROOT, student.image.name)
            if os.path.exists(image_path):
                os.remove(image_path)
        student.delete()
        deleted_count += 1
    
    # Redirect back to the view all page
    return redirect('view_all')
