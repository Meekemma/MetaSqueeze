import os
import logging
from celery import shared_task
from django.conf import settings
from django.core.files.base import ContentFile
from .models import DocumentFile
from .utils import (
    convert_pdf_to_word,
    convert_word_to_pdf,
    convert_pdf_to_text,
    convert_word_to_text
)

logger = logging.getLogger(__name__)

@shared_task
def document_convert(document_id):
    """
    Celery task to convert a document based on its conversion_type using utility functions.
    - Handles PDF <-> Word, and PDF/Word -> Text conversions.
    - Updates document status and handles errors gracefully.
    - Cleans up temporary output files after processing.
    """
    
    try:
        # Fetch the DocumentFile instance
        doc = DocumentFile.objects.get(id=document_id)
        doc.status = 'processing'
        doc.save()

        # Get the path and size of the uploaded file
        original_path = doc.original_file.path
        original_size = os.path.getsize(original_path)
        doc.original_size = original_size

        # Validate input file format against the conversion type
        expected_extensions = {
            'pdf_to_word': ['pdf'],
            'pdf_to_text': ['pdf'],
            'word_to_pdf': ['docx'],
            'word_to_text': ['docx'],
        }.get(doc.conversion_type, [])

        if expected_extensions and not original_path.lower().endswith(tuple(f'.{ext}' for ext in expected_extensions)):
            doc.status = 'failed'
            doc.error_message = f"Invalid input file format for {doc.conversion_type}. Expected: {', '.join(expected_extensions)}."
            doc.save()
            logger.error(f"Invalid file format for document {document_id}: {original_path}")
            return

        # Determine output file extension and filename
        extension = {
            'pdf_to_word': 'docx',
            'word_to_pdf': 'pdf',
            'pdf_to_text': 'txt',
            'word_to_text': 'txt',
        }.get(doc.conversion_type, 'bin')

        filename = f"{doc.id}.{extension}"
        output_path = os.path.join(settings.MEDIA_ROOT, 'documents/converted', filename)

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Select the appropriate conversion function
        logger.info(f"Starting conversion for document {document_id}: {doc.conversion_type}")
        conversion_functions = {
            'pdf_to_word': convert_pdf_to_word,
            'pdf_to_text': convert_pdf_to_text,
            'word_to_pdf': convert_word_to_pdf,
            'word_to_text': convert_word_to_text,
        }
        conversion_func = conversion_functions.get(doc.conversion_type)

        if not conversion_func:
            doc.status = 'failed'
            doc.error_message = f"Unsupported conversion type: {doc.conversion_type}"
            doc.save()
            logger.error(f"Unsupported conversion type for document {document_id}: {doc.conversion_type}")
            return

        # Run the conversion utility function
        conversion_func(original_path, output_path)

        # Ensure the output file was created
        if not os.path.exists(output_path):
            doc.status = 'failed'
            doc.error_message = "Conversion failed: Output file not created."
            doc.save()
            logger.error(f"Output file not created for document {document_id}: {output_path}")
            return

        # Save converted file to model's FileField
        relative_path = os.path.join('documents/converted', filename)
        with open(output_path, 'rb') as f:
            doc.converted_file.save(relative_path, ContentFile(f.read()))

        # Record the size of the converted file
        doc.converted_size = os.path.getsize(output_path)

        # Mark document as successfully converted
        doc.status = 'completed'
        doc.save()
        logger.info(f"Completed conversion for document {document_id}: {relative_path}")

        # Clean up temporary file after saving to model
        if os.path.exists(output_path):
            os.remove(output_path)
            logger.info(f"Removed temporary converted file: {output_path}")

    except DocumentFile.DoesNotExist:
        logger.error(f"Document {document_id} not found.")
        return

    except FileNotFoundError as e:
        doc.status = 'failed'
        doc.error_message = f"File not found: {str(e)}"
        doc.save()
        logger.error(f"File not found for document {document_id}: {str(e)}")
        return

    except Exception as e:
        doc.status = 'failed'
        doc.error_message = f"Conversion failed: {str(e)}"
        doc.save()
        logger.error(f"Error converting document {document_id}: {str(e)}", exc_info=True)
        return

    finally:
        # Ensure any leftover temp files are cleaned up if conversion wasn't completed
        if 'output_path' in locals() and os.path.exists(output_path) and doc.status != 'completed':
            try:
                os.remove(output_path)
                logger.info(f"Cleaned up temporary file after failure: {output_path}")
            except Exception as e:
                logger.warning(f"Failed to clean up temporary file {output_path}: {str(e)}")
