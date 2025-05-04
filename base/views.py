from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from .serializers import ImageSerializer
from base.tasks import optimize_image

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