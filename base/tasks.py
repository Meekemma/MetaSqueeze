import logging
from celery import shared_task
from PIL import Image
from PIL.ExifTags import TAGS
from django.core.files.base import ContentFile
from io import BytesIO
from .models import UploadedImage
from datetime import datetime
from datetime import timedelta
from django.utils.timezone import now

logger = logging.getLogger(__name__)

@shared_task
def optimize_image(image_id):
    try:
        # Fetch the image from the database
        uploaded_image = UploadedImage.objects.get(id=image_id)
        original_image_path = uploaded_image.original_image.path

        with Image.open(original_image_path) as img:
            # Store original image format and dimensions
            uploaded_image.format = img.format
            uploaded_image.width = img.width
            uploaded_image.height = img.height

            # Extract EXIF metadata
            exif_data = img._getexif() if img._getexif() else None
            if exif_data:
                for tag, value in exif_data.items():
                    tag_name = TAGS.get(tag, tag)
                    if tag_name == 'Make':
                        uploaded_image.camera_make = value
                    elif tag_name == 'Model':
                        uploaded_image.camera_model = value
                    elif tag_name == 'DateTime':
                        try:
                            uploaded_image.taken_at = datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
                        except ValueError:
                            logger.warning(f"Invalid DateTime format for image {image_id}: {value}")
                    elif tag_name == 'GPSLatitude' and isinstance(value, tuple):
                        ref = exif_data.get(TAGS.get('GPSLatitudeRef'), 'N')
                        uploaded_image.gps_latitude = convert_gps_to_decimal(*value, ref)
                    elif tag_name == 'GPSLongitude' and isinstance(value, tuple):
                        ref = exif_data.get(TAGS.get('GPSLongitudeRef'), 'E')
                        uploaded_image.gps_longitude = convert_gps_to_decimal(*value, ref)

            # Optimize image: resize to max 1024px while preserving aspect ratio
            max_size = 1024
            img.thumbnail((max_size, max_size), Image.LANCZOS)

            # Determine output format (default to WEBP if not specified)
            output_format = uploaded_image.output_format or 'WEBP'
            optimized_image_name = f"optimized_{uploaded_image.id}.{output_format.lower()}"
            optimized_image_io = BytesIO()

            # Save optimized image in the chosen format
            if output_format == 'WEBP':
                img.save(optimized_image_io, format='WEBP', quality=85)
            elif output_format == 'JPEG':
                # Convert to RGB if necessary (JPEG doesn't support transparency)
                if img.mode in ('RGBA', 'LA'):
                    img = img.convert('RGB')
                img.save(optimized_image_io, format='JPEG', quality=85, optimize=True)
            elif output_format == 'PNG':
                img.save(optimized_image_io, format='PNG', optimize=True)
            else:
                logger.error(f"Unsupported output format {output_format} for image {image_id}")
                return False

            # Save optimized image to model
            optimized_image_io.seek(0)
            uploaded_image.optimized_image.save(
                optimized_image_name,
                ContentFile(optimized_image_io.getvalue())
            )

            # Save updated model fields
            uploaded_image.save()
            img.close()

        return True

    except UploadedImage.DoesNotExist:
        logger.error(f"Image {image_id} not found.")
        return False
    except Exception as e:
        logger.error(f"Error optimizing image {image_id}: {e}", exc_info=True)
        return False

def convert_gps_to_decimal(degrees, minutes, seconds, direction):
    """
    Convert GPS coordinates to decimal degrees.
    """
    decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
    if direction in ['S', 'W']:
        decimal = -decimal
    return decimal



@shared_task
def cleanup_old_images():
    """
    Deletes images older than 30 days from the database and filesystem.
    """
    try:
        threshold_date = now() - timedelta(days=30)
        old_images = UploadedImage.objects.filter(uploaded_at__lt=threshold_date)

        deleted_count = 0  # ✅ Counter for deleted images

        for image in old_images:
            # Delete the image files from the filesystem
            if image.original_image:
                image.original_image.delete(save=False)
            if image.optimized_image:
                image.optimized_image.delete(save=False)

            # Delete the image record from the database
            image.delete()
            deleted_count += 1  # ✅ Increment after deletion

        logger.info(f"Deleted {deleted_count} old images.")
    except Exception as e:
        logger.error(f"Error during cleanup of old images: {e}", exc_info=True)
