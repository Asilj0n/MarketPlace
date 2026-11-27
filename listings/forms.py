from django import forms

from mysite.forms import BootstrapFormMixin, validate_image_size

from .models import Listing


class ListingForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'category', 'condition', 'price', 'campus', 'image']
        labels = {'image': 'Photo'}
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'price': forms.NumberInput(attrs={'min': 0}),
        }

    def clean_image(self):
        return validate_image_size(self.cleaned_data.get('image'))
