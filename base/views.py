from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from .serializers import ImageSerializer
from base.tasks import optimize_image
from django.http import FileResponse
from .models import UploadedImage





@api_view(['POST'])
def image_upload_view(request):
    """
    Handle image uploads and trigger asynchronous optimization.
    Accepts 'original_image' and optional 'output_format' (WEBP, JPEG, PNG).
    """
    serializer = ImageSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    uploaded_image = serializer.save()

    # Call Celery task to optimize the image in the background
    optimize_image.delay(uploaded_image.id)

    return Response({
        'message': 'Image uploaded successfully! Optimization in progress.',
        'data': serializer.data
    }, status=status.HTTP_201_CREATED)








@api_view(['GET'])
def image_list_view(request, image_id):
    """
    Retrieve and serve the optimized image for download by its ID.
    Returns the image file if optimized, or a status if pending/not found.
    """
    try:
        # Fetch only necessary fields to optimize query
        uploaded_image = UploadedImage.objects.only(
            'optimized_image', 'output_format'
        ).get(pk=image_id)
    except UploadedImage.DoesNotExist:
        return Response(
            {'error': 'Image not found.'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Check if optimization is complete
    if not uploaded_image.optimized_image:
        return Response(
            {'status': 'pending', 'message': 'Image optimization is still in progress.'},
            status=status.HTTP_202_ACCEPTED
        )

    # Serve the optimized image as a downloadable file
    file_path = uploaded_image.optimized_image.path
    file_name = f"optimized_{image_id}.{uploaded_image.output_format.lower()}"
    response = FileResponse(
        open(file_path, 'rb'),
        as_attachment=True,
        filename=file_name
    )
    return response