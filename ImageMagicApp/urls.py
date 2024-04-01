# upscaler_app/urls.py
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
#     path('backgroundremover', views.background_remover,
#          name='background_remover'),

    path('imagetovector', views.image_to_vector, name='image_to_vector'),

    path('svgtoeps', views.svg_to_eps, name='svg_to_eps'),

    path('upload/', views.upload_image, name='upload_image'),

    path('upscaled-image/', views.upscaledimage, name='upscaledimage'),

    # image to victor
    path('imagetovictor/', views.imagetovictor,
         name='imagetovictor'),
    # image to svgToeps
    path('svgToeps/', views.svgToeps,
         name='svgToeps'),
    path('image/<int:pk>/', views.image_detail, name='image_detail'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
