import logging
from celery import shared_task
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from datetime import timedelta
from django.utils.timezone import now

logger = logging.getLogger(__name__)

@shared_task
def cleanup_blacklisted_tokens():
    """
    Cleans up blacklisted tokens older than 7 days.
    """
    expiration_time = now() - timedelta(days=7)
    expired_tokens = BlacklistedToken.objects.filter(
        blacklisted_at__lt=expiration_time
    )
    deleted_count = 0

    for token in expired_tokens:
        try:
            token.delete()
            deleted_count += 1
        except Exception as e:
            logger.error(f"Error deleting token {token}: {e}", exc_info=True)

    logger.info(f"Deleted {deleted_count} blacklisted tokens older than 7 days.")
