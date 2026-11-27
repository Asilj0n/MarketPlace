from django import forms
from django.conf import settings


class BootstrapFormMixin:
    """Adds Bootstrap 5 classes to every widget so templates can just render fields."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                css = 'form-check-input'
            elif isinstance(widget, forms.Select):
                css = 'form-select'
            else:
                css = 'form-control'
            widget.attrs['class'] = f"{widget.attrs.get('class', '')} {css}".strip()


def validate_image_size(image):
    """Reject uploads larger than MAX_UPLOAD_SIZE_MB."""
    limit = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if image and getattr(image, 'size', 0) > limit:
        raise forms.ValidationError(
            f'The photo is too large. The maximum size is {settings.MAX_UPLOAD_SIZE_MB} MB.'
        )
    return image
