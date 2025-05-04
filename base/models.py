from django.db import models
import os

class UploadedImage(models.Model):
    # Choices for output_format field
    OUTPUT_FORMAT_CHOICES = [
        ('WEBP', 'WEBP'),
        ('JPEG', 'JPEG'),
        ('PNG', 'PNG'),
    ]

    original_image = models.ImageField(upload_to='images/originals/')
    optimized_image = models.ImageField(upload_to='images/optimized/', null=True, blank=True)
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    format = models.CharField(max_length=10, null=True, blank=True)  
    camera_make = models.CharField(max_length=100, null=True, blank=True)
    camera_model = models.CharField(max_length=100, null=True, blank=True)
    taken_at = models.DateTimeField(null=True, blank=True)
    gps_latitude = models.FloatField(null=True, blank=True)
    gps_longitude = models.FloatField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    output_format = models.CharField(
        max_length=10,
        choices=OUTPUT_FORMAT_CHOICES,
        null=True,
        blank=True,
        default='WEBP'
    )  
    def __str__(self):
        return f"Image {self.id} - {os.path.basename(self.original_image.name)}"

    class Meta:
        ordering = ['-uploaded_at']
        indexes = [models.Index(fields=['uploaded_at'])]