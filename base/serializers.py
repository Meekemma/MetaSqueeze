from rest_framework import serializers
from .models import UploadedImage

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedImage
        fields = [
            'id',
            'original_image',
            'optimized_image',
            'width',
            'height',
            'format',
            'camera_make',
            'camera_model',
            'taken_at',
            'gps_latitude',
            'gps_longitude',
            'uploaded_at',
            'output_format',
        ]
        read_only_fields = [
            'id',
            'optimized_image',
            'width',
            'height',
            'format',
            'camera_make',
            'camera_model',
            'taken_at',
            'gps_latitude',
            'gps_longitude',
            'uploaded_at',
        ]

    def validate_output_format(self, value):
        """
        Validate that output_format is one of the supported formats (WEBP, JPEG, PNG).
        """
        if value and value not in dict(UploadedImage.OUTPUT_FORMAT_CHOICES).keys():
            raise serializers.ValidationError(
                "Invalid output format. Supported formats: WEBP, JPEG, PNG."
            )
        return value



    def validate_original_image(self, value):
        """
        Validate the uploaded image for size and format.
        """
        max_size = 10 * 1024 * 1024  # 10MB
        if value.size > max_size:
            raise serializers.ValidationError("Image file too large (max 10MB).")
        if not value.name.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            raise serializers.ValidationError(
                "Unsupported image format. Use PNG, JPG, or WEBP."
            )
        return value