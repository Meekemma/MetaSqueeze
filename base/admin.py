from django.contrib import admin
from django.contrib import admin
from .models import UploadedImage



@admin.register(UploadedImage)
class UploadedImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'original_image', 'optimized_image', 'width', 'height', 'uploaded_at']


# Register your models here.
