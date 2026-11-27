import re

from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from .models import normalize_phone_number


def registration_data(**overrides):
    data = {
        'username': 'asiljon',
        'email': 'asiljon.mamajonov_2029@ucentralasia.org',
        'campus': 'naryn',
        'whatsapp_number': '+996 555 123 456',
        'password1': 'Str0ng-pass-123',
        'password2': 'Str0ng-pass-123',
    }
    data.update(overrides)
    return data


class RegistrationTests(TestCase):
    def test_university_email_registers_inactive_user_and_sends_link(self):
        response = self.client.post(reverse('register'), registration_data())
        self.assertRedirects(response, reverse('login'))

        user = User.objects.get(username='asiljon')
        self.assertFalse(user.is_active)
        self.assertEqual(user.profile.campus, 'naryn')
        self.assertEqual(user.profile.whatsapp_number, '+996555123456')
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('/activate/', mail.outbox[0].body)

    def test_email_from_other_domain_is_rejected(self):
        for email in ['someone@gmail.com', 'someone@ucentralasia.org.evil.com', 'x@fakeucentralasia.org']:
            response = self.client.post(reverse('register'), registration_data(email=email))
            self.assertContains(response, 'Please use your university email address')
        self.assertFalse(User.objects.exists())

    def test_email_is_case_insensitive_and_must_be_unique(self):
        self.client.post(reverse('register'), registration_data(email='A.B_2029@UCentralAsia.org'))
        self.assertEqual(User.objects.get().email, 'a.b_2029@ucentralasia.org')

        response = self.client.post(
            reverse('register'), registration_data(username='other', email='a.b_2029@ucentralasia.org')
        )
        self.assertContains(response, 'already exists')

    def test_invalid_whatsapp_number_is_rejected(self):
        response = self.client.post(reverse('register'), registration_data(whatsapp_number='call me'))
        self.assertContains(response, 'valid WhatsApp number')


class ActivationTests(TestCase):
    def register_and_get_link(self):
        self.client.post(reverse('register'), registration_data())
        return re.search(r'https?://\S+/activate/\S+/', mail.outbox[0].body).group(0)

    def test_inactive_user_cannot_log_in(self):
        self.client.post(reverse('register'), registration_data())
        response = self.client.post(reverse('login'), {'username': 'asiljon', 'password': 'Str0ng-pass-123'})
        self.assertContains(response, 'activate your account')

    def test_activation_link_activates_and_logs_in_once(self):
        link = self.register_and_get_link()
        response = self.client.get(link)
        self.assertRedirects(response, reverse('listings:index'))
        self.assertTrue(User.objects.get().is_active)

        self.client.logout()
        response = self.client.get(link, follow=True)
        self.assertContains(response, 'invalid or has already been used')

    def test_bad_token_is_rejected(self):
        self.client.post(reverse('register'), registration_data())
        response = self.client.get(reverse('activate', args=['MQ', 'bad-token']), follow=True)
        self.assertContains(response, 'invalid or has already been used')
        self.assertFalse(User.objects.get().is_active)


class ProfileTests(TestCase):
    def test_profile_update(self):
        user = User.objects.create_user('sam', 'sam@ucentralasia.org', 'pw')
        self.client.force_login(user)
        response = self.client.post(reverse('profile'), {'campus': 'khorog', 'whatsapp_number': '+992 90 123 4567'})
        self.assertRedirects(response, reverse('profile'))
        user.profile.refresh_from_db()
        self.assertEqual(user.profile.campus, 'khorog')
        self.assertEqual(user.profile.whatsapp_digits, '992901234567')

    def test_phone_normalization(self):
        self.assertEqual(normalize_phone_number('+996 (555) 12-34-56'), '+996555123456')
        self.assertEqual(normalize_phone_number('996555123456'), '+996555123456')
