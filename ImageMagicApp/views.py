# views.py
import os
import cv2
import io
import rembg
from io import BytesIO
# import potrace
from django.http import HttpResponseBadRequest
from django.core.files.base import ContentFile
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from .models import UploadedImage
from .forms import ImageUploadForm
from PIL import Image
from django.conf import settings
from django.core.files.base import ContentFile
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
import cv2
from PIL import Image
import uuid
import time
from django.core.files.base import ContentFile
from urllib.parse import urljoin
# for download


def home(request):
    form = ImageUploadForm()
    return render(request, 'home.html', {'form': form})


def background_remover(request):
    return render(request, 'background_remover.html')


def image_to_vector(request):
    form = ImageUploadForm()
    return render(request, 'image_to_vector.html', {'form': form})


def svg_to_eps(request):
    form = ImageUploadForm()
    return render(request, 'svg_to_eps.html', {'form': form})


def upscaledimage(request):
    form = ImageUploadForm()
    return render(request, 'upscaled_image.html', {'form': form})


def upload_image(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            upscale_factor = int(request.POST.get('upscale'))
            image = form.save()
            try:
                # Upscale the image
                upscale_image(image, upscale_factor)

                # Set the image URL for download
                image_url = image.image.url

                # Pass the image URL to home.html
                return render(request, 'upscaled_now_download.html', {'image_url': image_url})
            except Exception as e:
                error_message = "Error upscaling the image: " + str(e)
                return HttpResponseBadRequest(error_message)
        else:
            # Form is not valid, handle the form errors here
            error_message = "Error: File formate not supported. Please use another image!."
            return HttpResponseBadRequest(error_message)
    else:
        form = ImageUploadForm()
    return render(request, 'home.html', {'form': form})


def upscale_image(image, upscale_factor):
    img = Image.open(image.image.path)

    # Generate a unique filename for the upscaled image
    unique_name = f"upscaled_{str(uuid.uuid4())}.jpg"

    # Calculate the new width and height
    new_width = img.width * upscale_factor
    new_height = img.height * upscale_factor

    # Resize the image with the LANCZOS filter for higher quality
    img = img.resize((new_width, new_height), Image.LANCZOS)

    # Save the upscaled image in the uploaded_images directory
    upscale_path = os.path.join('media', 'uploaded_images', unique_name)
    img.save(upscale_path, format='JPEG')

    # Update the image object with the path to the upscaled image
    image.upscale_image = os.path.join('uploaded_images', unique_name)
    image.save()


def image_detail(request, pk):
    image = UploadedImage.objects.get(pk=pk)
    return render(request, 'home.html', {'image': image})
# download function

# end download


def download_upscaled_image(request, pk):
    image = UploadedImage.objects.get(pk=pk)
    file_path = image.upscale_image.path

    with open(file_path, 'rb') as file:
        response = FileResponse(file)

        # Get the original file extension from the file name
        _, original_extension = os.path.splitext(os.path.basename(file_path))

        # Set the content type based on the original file's extension
        content_type = f'image/{original_extension.lstrip(".")}'
        response['Content-Type'] = content_type

        # Set the content disposition with the original extension
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
        return response
# end download function


def background_remove_view(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Get the uploaded image from the form
            uploaded_image = form.cleaned_data['image']

            # Check if the uploaded file is an image (you may want to add more robust validation)
            if not uploaded_image.name.endswith(('.jpg', '.jpeg', '.png')):
                return HttpResponse("Invalid image format. Please upload a JPG or PNG file.")

            # Read the uploaded image using Pillow
            img = Image.open(uploaded_image)

            # Convert the image to RGBA mode (if it's not already)
            if img.mode != "RGBA":
                img = img.convert("RGBA")

            # Use Rembg to remove the background
            with rembg.remove(img) as output:
                output_bytes = io.BytesIO()
                output.save(output_bytes, format="PNG")

            # Define the relative path for storing the processed images in MEDIA_ROOT
            relative_path = 'uploaded_images/'

            # Join MEDIA_ROOT with the relative path to get the full storage path
            storage_path = os.path.join(settings.MEDIA_ROOT, relative_path)

            # Ensure the storage directory exists, and create it if necessary
            os.makedirs(storage_path, exist_ok=True)

            # Generate a unique filename, e.g., using the original file's name
            filename = uploaded_image.name

            # Construct the full path to save the processed image
            processed_image_path = os.path.join(storage_path, filename)

            # Save the processed image
            with open(processed_image_path, 'wb') as processed_image_file:
                processed_image_file.write(output_bytes.getvalue())

            # Create a new instance of UploadedImage with the processed image path
            processed_image = UploadedImage.objects.create(
                image=uploaded_image,
                upscale_image=os.path.join(relative_path, filename)
            )

            # Return a success message and the URL of the processed image
            processed_image_url = os.path.join(
                '/media', relative_path, filename)
            msg = "Image Background removed!"
            return render(request, 'bgremove_download.html', {'form': form, 'msg': msg, 'processed_image_url': processed_image_url})
    else:
        form = ImageUploadForm()
    return render(request, 'background_remover.html', {'form': form})
# image to victor


def imagetovictor(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Manually set the image field with a unique filename
            unique_id = str(uuid.uuid4())
            unique_filename = f'{unique_id}_{form.cleaned_data["image"].name}'

            # Read the file content
            file_content = request.FILES['image'].file.read()

            # Create a ContentFile with the file content and the unique filename
            content_file = ContentFile(file_content)
            content_file.name = unique_filename

            # Save the uploaded image to the database
            uploaded_image = form.save(commit=False)
            uploaded_image.image = content_file
            uploaded_image.save()

            # Get the path to the uploaded image file
            image_path = uploaded_image.image.path

            # Perform image processing (optional)
            # For example, you can apply Gaussian blur to reduce noise
            img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
            img = cv2.GaussianBlur(img, (5, 5), 0)

            # Save the processed image to the folder with the processed filename
            processed_filename = f'output_vector_{unique_filename}'
            processed_image_path = os.path.join(
                settings.MEDIA_ROOT, 'uploaded_images', processed_filename)
            cv2.imwrite(processed_image_path, img)

            # Update the 'upscale_image' field with the processed filename
            uploaded_image.upscale_image = processed_filename
            uploaded_image.save()

            # Construct the URL for the processed image
            processed_image_url = urljoin(
                '/media/uploaded_images/', processed_filename)

            return render(request, 'imagetovector_download.html', {'form': form, 'processed_image_url': processed_image_url})
    else:
        form = ImageUploadForm()

    return render(request, 'imagetovector_download.html', {'form': form})

# svg image to EPS


def svgToeps(request):
    if request.method == 'POST' and request.FILES.get('image'):
        uploaded_svg = request.FILES['image']

        # Check if the uploaded file is an SVG
        if uploaded_svg.name.endswith('.svg'):
            # Generate a unique filename for the EPS file
            unique_filename = f"{uuid.uuid4().hex}.eps"

            # Convert SVG to EPSac
            drawing = svg2rlg(uploaded_svg)
            eps_file = ContentFile(b'', name=unique_filename)
            renderPDF.drawToFile(drawing, eps_file)

            # Save the EPS file to the media folder and database
            uploaded_image = UploadedImage(image=eps_file)
            uploaded_image.save()

            # Debug: Print the path where the image is stored
            print("Stored image path:", uploaded_image.image.path)

            # Pass the uploaded_image to the template context
            context = {'uploaded_image': uploaded_image}

            # Render the template with the context
            return render(request, 'eps_file_download.html', context)

        else:
            # Return an error message if the file is not an SVG
            return JsonResponse({'error': 'Uploaded file is not an SVG.'}, status=400)
    else:
        # Return an error message for invalid requests
        return JsonResponse({'error': 'Invalid request.'}, status=400)
