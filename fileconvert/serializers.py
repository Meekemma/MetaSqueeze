from rest_framework import serializers
from .models import DocumentFile

class DocumentFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentFile
        fields = [
            'id',
            'uploaded_at',
            'original_file',
            'converted_file',
            'conversion_type',
            'status',
            'error_message',
            'original_size',
            'converted_size',
        ]
        read_only_fields = [
            'id',
            'uploaded_at',
            'converted_file',
            'status',
            'error_message',
            'original_size',
            'converted_size',
        ]

    def validate_conversion_type(self, value):
        """
        Validate that conversion_type is one of the supported types.
        """
        if value and value not in dict(DocumentFile.CONVERSION_CHOICES).keys():
            raise serializers.ValidationError(
                "Invalid conversion type. Supported types: PDF to Word, Word to PDF, PDF to Text, Word to Text."
            )
        return value.lower()  # Normalize to lowercase for consistency

    def validate_original_file(self, value):
        """
        Validate the uploaded file format and ensure it matches conversion_type.
        """
        if not value.name.lower().endswith(('.pdf', '.docx', '.txt')):
            raise serializers.ValidationError(
                "Unsupported file format. Use PDF, DOCX, or TXT."
            )

        # Ensure file extension matches conversion_type
        conversion_type = self.initial_data.get('conversion_type')
        if conversion_type:
            expected_extensions = {
                'pdf_to_word': ['pdf'],
                'pdf_to_text': ['pdf'],
                'word_to_pdf': ['docx'],
                'word_to_text': ['docx'],
            }.get(conversion_type, [])
            if expected_extensions and not value.name.lower().endswith(tuple(f'.{ext}' for ext in expected_extensions)):
                raise serializers.ValidationError(
                    f"File format does not match conversion type. For {conversion_type}, use {', '.join(expected_extensions)}."
                )

        return value