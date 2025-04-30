from django.shortcuts import render, redirect
from .forms import StudentForm
from .models import Student
from PIL import Image, ImageDraw, ImageFont
from django.http import FileResponse
import os
from django.conf import settings

def home(request):
    return render(request, 'id_card_app/index.html')

def new_id_card(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save(commit=False)

            template_path = os.path.join(settings.BASE_DIR, 'id_card_app/static/zza_idcardTemplate.png')
            # Load template
            template = Image.open("zza_idcardTemplate.png").convert("RGBA")
            img = Image.open(template_path)
            draw = ImageDraw.Draw(template)

            font_path = os.path.join(settings.BASE_DIR, 'id_card_app/static/fonts/Poppins-Regular.ttf')
            font = ImageFont.truetype(font_path, 20)

            # Adjusted positions (example values)
            draw.text((50, 60), f"Name: {data['name']}", font=font, fill="black")
            draw.text((50, 100), f"Father: {data['father']}", font=font, fill="black")
            draw.text((50, 140), f"Mother: {data['mother']}", font=font, fill="black")
            draw.text((50, 180), f"Class: {data['class']}", font=font, fill="black")
            draw.text((50, 220), f"Section: {data['section']}", font=font, fill="black")
            draw.text((50, 260), f"Roll No: {data['roll']}", font=font, fill="black")
            draw.text((50, 300), f"Mobile: {data['mobile']}", font=font, fill="black")

            
            # Save as PNG or JPG
            output_path = "id_card_output.png"
            template.save(output_path)
            print(f"Saved to: {output_path}")

            filename = f"{student.name}_{student.roll_no}.png"
            save_path = os.path.join(settings.MEDIA_ROOT, 'cards', filename)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            img.save(save_path)

            student.image = f"cards/{filename}"
            student.save()
            return redirect('view_all')
    else:
        form = StudentForm()
    return render(request, 'id_card_app/form.html', {'form': form})

def view_all(request):
    students = Student.objects.all()
    return render(request, 'id_card_app/view_all.html', {'students': students})

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
