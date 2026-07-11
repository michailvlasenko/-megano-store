from django.core.validators import validate_email as django_validate_email
from django.core.exceptions import ValidationError
import re


def validate_email(value):
    if not value:
        return False
    try:
        django_validate_email(value)
        return True
    except ValidationError:
        return False


def validate_phone(value):
    if not value:
        return False
    cleaned = re.sub(r'[\s\-\+\(\)]', '', value)
    return cleaned.isdigit() and 7 <= len(cleaned) <= 20


def validate_password(value):
    return len(value) >= 6


def validate_required(value):
    return bool(value and str(value).strip())
