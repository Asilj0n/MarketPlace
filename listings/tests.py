import shutil
import tempfile

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Listing

# A valid 1x1 GIF, so ImageField validation passes.
TINY_GIF = (
    b'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00'
    b',\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
)


def make_user(username, whatsapp='+996555000111', campus='naryn'):
    user = User.objects.create_user(username, f'{username}@ucentralasia.org', 'pw')
    user.profile.whatsapp_number = whatsapp
    user.profile.campus = campus
    user.profile.save()
    return user


def make_listing(seller, **overrides):
    fields = {
        'title': 'Calculus textbook',
        'description': 'Stewart, 8th edition',
        'category': Listing.Category.TEXTBOOKS,
        'price': 500,
        'campus': 'naryn',
    }
    fields.update(overrides)
    return Listing.objects.create(seller=seller, **fields)


class AccessTests(TestCase):
    def test_pages_require_login(self):
        listing = make_listing(make_user('seller'))
        for url in [reverse('listings:index'), listing.get_absolute_url(), reverse('listings:create')]:
            response = self.client.get(url)
            self.assertRedirects(response, f"{reverse('login')}?next={url}")


class BrowseTests(TestCase):
    def setUp(self):
        self.seller = make_user('seller')
        self.client.force_login(make_user('buyer'))

    def test_sold_listings_hidden_unless_requested(self):
        make_listing(self.seller, title='Lamp')
        make_listing(self.seller, title='Old chair', status=Listing.Status.SOLD)

        response = self.client.get(reverse('listings:index'))
        self.assertContains(response, 'Lamp')
        self.assertNotContains(response, 'Old chair')

        response = self.client.get(reverse('listings:index'), {'show_sold': '1'})
        self.assertContains(response, 'Old chair')

    def test_filters(self):
        make_listing(self.seller, title='Free jacket', category='clothing', price=0, campus='khorog')
        make_listing(self.seller, title='Laptop', category='electronics', price=30000)

        def titles(**params):
            response = self.client.get(reverse('listings:index'), params)
            return {listing.title for listing in response.context['listings']}

        self.assertEqual(titles(free='1'), {'Free jacket'})
        self.assertEqual(titles(category='electronics'), {'Laptop'})
        self.assertEqual(titles(campus='khorog'), {'Free jacket'})
        self.assertEqual(titles(q='lap'), {'Laptop'})
        self.assertEqual(titles(category='not-a-category'), {'Free jacket', 'Laptop'})

    def test_detail_shows_whatsapp_link_to_buyer(self):
        listing = make_listing(self.seller)
        response = self.client.get(listing.get_absolute_url())
        self.assertContains(response, 'https://wa.me/996555000111?text=')
        self.assertNotContains(response, 'Manage your listing')

    def test_free_listing_shows_free(self):
        listing = make_listing(self.seller, price=0)
        self.assertContains(self.client.get(listing.get_absolute_url()), 'Free')


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class SellTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        from django.conf import settings
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_create_listing_with_photo(self):
        user = make_user('seller')
        self.client.force_login(user)
        response = self.client.post(reverse('listings:create'), {
            'title': 'Desk lamp',
            'description': 'Works fine',
            'category': 'furniture',
            'condition': 'good',
            'price': 0,
            'campus': 'naryn',
            'image': SimpleUploadedFile('lamp.gif', TINY_GIF, content_type='image/gif'),
        })
        listing = Listing.objects.get()
        self.assertRedirects(response, listing.get_absolute_url())
        self.assertEqual(listing.seller, user)
        self.assertEqual(listing.status, Listing.Status.AVAILABLE)
        self.assertTrue(listing.is_free)
        self.assertTrue(listing.image.name.startswith('listings/'))

    def test_negative_price_rejected(self):
        self.client.force_login(make_user('seller'))
        response = self.client.post(reverse('listings:create'), {
            'title': 'X', 'description': 'Y', 'category': 'other',
            'condition': 'good', 'price': -5, 'campus': 'naryn',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Listing.objects.exists())

    def test_seller_without_whatsapp_is_sent_to_profile(self):
        self.client.force_login(make_user('seller', whatsapp=''))
        self.assertRedirects(self.client.get(reverse('listings:create')), reverse('profile'))


class OwnershipTests(TestCase):
    def setUp(self):
        self.seller = make_user('seller')
        self.other = make_user('other')
        self.listing = make_listing(self.seller)

    def test_other_users_cannot_edit_delete_or_change_status(self):
        self.client.force_login(self.other)
        pk = self.listing.pk
        self.assertEqual(self.client.get(reverse('listings:update', args=[pk])).status_code, 404)
        self.assertEqual(self.client.post(reverse('listings:delete', args=[pk])).status_code, 404)
        response = self.client.post(reverse('listings:update_status', args=[pk]), {'status': 'sold'})
        self.assertEqual(response.status_code, 404)

        self.listing.refresh_from_db()
        self.assertEqual(self.listing.status, Listing.Status.AVAILABLE)

    def test_seller_can_change_status(self):
        self.client.force_login(self.seller)
        url = reverse('listings:update_status', args=[self.listing.pk])
        self.client.post(url, {'status': 'reserved'})
        self.listing.refresh_from_db()
        self.assertEqual(self.listing.status, Listing.Status.RESERVED)

        self.client.post(url, {'status': 'bogus'})
        self.listing.refresh_from_db()
        self.assertEqual(self.listing.status, Listing.Status.RESERVED)

    def test_status_change_requires_post(self):
        self.client.force_login(self.seller)
        response = self.client.get(reverse('listings:update_status', args=[self.listing.pk]))
        self.assertEqual(response.status_code, 405)

    def test_seller_can_edit_and_delete(self):
        self.client.force_login(self.seller)
        response = self.client.get(self.listing.get_absolute_url())
        self.assertContains(response, 'Manage your listing')

        self.client.post(reverse('listings:update', args=[self.listing.pk]), {
            'title': 'Calculus textbook (cheaper!)', 'description': 'Stewart', 'category': 'textbooks',
            'condition': 'good', 'price': 300, 'campus': 'naryn',
        })
        self.listing.refresh_from_db()
        self.assertEqual(self.listing.price, 300)

        response = self.client.post(reverse('listings:delete', args=[self.listing.pk]))
        self.assertRedirects(response, reverse('profile'))
        self.assertFalse(Listing.objects.exists())
