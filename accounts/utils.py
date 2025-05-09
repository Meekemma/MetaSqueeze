from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes


def send_verification_email(user, request):
    """
    Sends a verification email to the user after registration.
    """
    token = default_token_generator.make_token(user)
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

    verify_url = request.build_absolute_uri(
        reverse('verify_email', kwargs={'uidb64': uidb64, 'token': token})
    )

    context = {
        'user': user,
        'verify_url': verify_url,
    }

    email_html_message = render_to_string('email/verify_email.html', context)
    email_plaintext_message = render_to_string('email/verify_email.txt', context)

    msg = EmailMultiAlternatives(
        subject="Verify your email address",
        body=email_html_message,
        from_email=settings.EMAIL_HOST_USER,
        to=[user.email],
    )
    msg.attach_alternative(email_html_message, "text/html")
    msg.send()
