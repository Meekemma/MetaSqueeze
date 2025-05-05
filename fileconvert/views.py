from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from .serializers import DocumentFileSerializer
from .tasks import document_convert
from django.http import FileResponse
from .models import DocumentFile


# Create your views here.

@api_view(['POST'])
def document_upload_view(request):
    """
    Handle document uploads and trigger asynchronous conversion.
    Accepts 'original_file' and optional 'output_format' (PDF, DOCX, TXT).
    """
    serializer = DocumentFileSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    uploaded_file = serializer.save()

    # Call Celery task to convert the document in the background
    document_convert.delay(uploaded_file.id)

    return Response({
        'message': 'Document uploaded successfully! Conversion in progress.',
        'data': serializer.data
    }, status=status.HTTP_201_CREATED)



@api_view(['GET'])
def document_download_view(request, document_id):
    """
    Serve the converted document for download by its ID.
    Returns the file if conversion is complete, or a status if pending/not found.
    """
    try:
        document = DocumentFile.objects.only(
            'converted_file', 'conversion_type', 'status'
        ).get(id=document_id)
    except DocumentFile.DoesNotExist:
        return Response(
            {'error': 'Document not found.'},
            status=status.HTTP_404_NOT_FOUND
        )

    if document.status == 'failed':
        return Response(
            {'status': 'failed', 'message': document.error_message or 'Conversion failed.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if document.status in ('pending', 'processing') or not document.converted_file:
        return Response(
            {'status': 'pending', 'message': 'Document conversion is still in progress.'},
            status=status.HTTP_202_ACCEPTED
        )

    # Serve the converted document as a downloadable file
    file_path = document.converted_file.path
    file_extension = {
        'pdf_to_word': 'docx',
        'word_to_pdf': 'pdf',
        'pdf_to_text': 'txt',
        'word_to_text': 'txt',
    }.get(document.conversion_type, 'bin')
    file_name = f"converted_{document_id}.{file_extension}"
    response = FileResponse(
        open(file_path, 'rb'),
        as_attachment=True,
        filename=file_name
    )
    return response