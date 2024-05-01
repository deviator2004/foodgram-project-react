import re

from django.conf import settings
from django.core.exceptions import ValidationError


def username_validator(value):
    unmatched = re.sub(r'^[\w.@+-]+', "", value)
    if value in settings.FORBIDDEN_USERNAMES:
        raise ValidationError(f"Имя пользователя {value} использовать нельзя!")
    elif value in unmatched:
        raise ValidationError(
            f"Имя пользователя не должно содержать {unmatched}"
        )
    return value
