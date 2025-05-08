import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class CustomPasswordValidator:
    def validate(self, password, user=None):
        if len(password) < 10: 
            raise ValidationError(
                _("This password is too short. It must contain at least 10 characters."),
                code='password_too_short',
            )

        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                _("This password must contain at least one uppercase letter."),
                code='password_no_uppercase',
            )

        if not re.search(r'[a-z]', password):
            raise ValidationError(
                _("This password must contain at least one lowercase letter."),
                code='password_no_lowercase',
            )

        if not re.search(r'[0-9]', password):
            raise ValidationError(
                _("This password must contain at least one digit."),
                code='password_no_digit',
            )

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError(
                _("This password must contain at least one special character."),
                code='password_no_special',
            )

        if user:
            if user.email.lower() in password.lower():
                raise ValidationError(
                    _("The password cannot contain the email address."),
                    code='password_contains_email',
                )
            if user.first_name and user.first_name.lower() in password.lower():
                raise ValidationError(
                    _("The password cannot contain your first name."),
                    code='password_contains_first_name',
                )
            if user.last_name and user.last_name.lower() in password.lower():
                raise ValidationError(
                    _("The password cannot contain your last name."),
                    code='password_contains_last_name',
                )

    def get_help_text(self):
        return _(
            "Your password must be at least 10 characters long and include an uppercase letter, "
            "lowercase letter, digit, and special character. It should not contain your name or email."
        )
