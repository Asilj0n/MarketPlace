from urllib.parse import quote

from django.conf import settings
from django.db import models
from django.urls import reverse

from users.models import CAMPUS_CURRENCY, Campus


class Listing(models.Model):
    class Category(models.TextChoices):
        TEXTBOOKS = 'textbooks', 'Textbooks & study materials'
        ELECTRONICS = 'electronics', 'Electronics'
        FURNITURE = 'furniture', 'Dorm & furniture'
        CLOTHING = 'clothing', 'Clothing & accessories'
        SPORTS = 'sports', 'Sports & outdoors'
        OTHER = 'other', 'Other'

    class Condition(models.TextChoices):
        NEW = 'new', 'New'
        LIKE_NEW = 'like_new', 'Like new'
        GOOD = 'good', 'Good'
        FAIR = 'fair', 'Fair'

    class Status(models.TextChoices):
        AVAILABLE = 'available', 'Available'
        RESERVED = 'reserved', 'Reserved'
        SOLD = 'sold', 'Sold'

    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='listings'
    )
    title = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=Category.choices)
    condition = models.CharField(max_length=20, choices=Condition.choices, default=Condition.GOOD)
    price = models.PositiveIntegerField(help_text='Enter 0 to give the item away for free.')
    campus = models.CharField(
        max_length=20, choices=Campus.choices, help_text='Where buyers can pick the item up.'
    )
    image = models.ImageField(upload_to='listings', blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.AVAILABLE, db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('listings:detail', kwargs={'pk': self.pk})

    @property
    def is_free(self):
        return self.price == 0

    @property
    def currency(self):
        return CAMPUS_CURRENCY.get(self.campus, '')

    @property
    def status_badge(self):
        """Bootstrap colour for the status badge."""
        return {
            self.Status.AVAILABLE: 'success',
            self.Status.RESERVED: 'warning',
            self.Status.SOLD: 'secondary',
        }[self.status]

    def whatsapp_url(self, request=None):
        """wa.me link to the seller, with a ready-made first message."""
        digits = self.seller.profile.whatsapp_digits
        if not digits:
            return ''
        text = f'Hi! I saw your listing "{self.title}" on MarketPlace. Is it still available?'
        if request is not None:
            text += ' ' + request.build_absolute_uri(self.get_absolute_url())
        return f'https://wa.me/{digits}?text={quote(text)}'
