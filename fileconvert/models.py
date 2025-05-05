from django.db import models
from django.core.validators import FileExtensionValidator
import os
import uuid

def upload_to_original(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('documents/originals/', filename)

def upload_to_converted(instance, filename):
    # Map conversion_type to the correct output extension
    extension = {
        'pdf_to_word': 'docx',
        'word_to_pdf': 'pdf',
        'pdf_to_text': 'txt',
        'word_to_text': 'txt',
    }.get(instance.conversion_type, 'bin')
    filename = f"{uuid.uuid4()}.{extension}"
    return os.path.join('documents/converted/', filename)




class DocumentFile(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    CONVERSION_CHOICES = [
        ('pdf_to_word', 'PDF to Word'),
        ('word_to_pdf', 'Word to PDF'),
        ('pdf_to_text', 'PDF to Text'),
        ('word_to_text', 'Word to Text'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    original_file = models.FileField(
        upload_to=upload_to_original,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'docx', 'txt'])]
    )
    converted_file = models.FileField(
        upload_to=upload_to_converted,
        blank=True,
        null=True
    )
    conversion_type = models.CharField(max_length=20, choices=CONVERSION_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.CharField(max_length=255, blank=True, null=True)
    original_size = models.BigIntegerField(null=True, blank=True)
    converted_size = models.BigIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.get_conversion_type_display()} ({self.id})"

    class Meta:
        verbose_name = 'Document File'
        verbose_name_plural = 'Document Files'
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['uploaded_at']),
            models.Index(fields=['status'])
        ]