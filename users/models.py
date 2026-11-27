import re

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models


class Campus(models.TextChoices):
    NARYN = 'naryn', 'Naryn'
    KHOROG = 'khorog', 'Khorog'
    TEKELI = 'tekeli', 'Tekeli'


# Local currency for prices listed on each campus.
CAMPUS_CURRENCY = {
    Campus.NARYN: 'KGS',
    Campus.KHOROG: 'TJS',
    Campus.TEKELI: 'KZT',
}


def normalize_phone_number(value):
    """Turn '+996 (555) 12-34-56' into '+996555123456', or raise ValidationError."""
    cleaned = re.sub(r'[\s\-().]', '', value or '')
    if not re.fullmatch(r'\+?\d{9,15}', cleaned):
        raise ValidationError(
            'Enter a valid WhatsApp number with the country code, e.g. +996 555 123 456.'
        )
    return '+' + cleaned.lstrip('+')


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='profile_pictures', blank=True)
    campus = models.CharField(max_length=20, choices=Campus.choices, blank=True)
    whatsapp_number = models.CharField(
        max_length=20,
        blank=True,
        help_text='Include the country code, e.g. +996 555 123 456.',
    )

    def __str__(self):
        return self.user.username

    @property
    def whatsapp_digits(self):
        """The number as wa.me links expect it: digits only, no '+'."""
        return re.sub(r'\D', '', self.whatsapp_number)
