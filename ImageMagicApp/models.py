from django.db import models


class UploadedImage(models.Model):
    image = models.ImageField(upload_to='uploaded_images/')
    upscale_image = models.ImageField(
        upload_to='upscaled_images/', blank=True, default='default_upscale_image.jpg')
    upscaled_image_data = models.BinaryField(blank=True, null=True)
