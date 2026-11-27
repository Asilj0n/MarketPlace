from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from .forms import ProfileForm, RegisterForm


def send_activation_email(request, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    activation_url = request.build_absolute_uri(reverse('activate', args=[uid, token]))
    message = render_to_string('users/activation_email.txt', {
        'user': user,
        'activation_url': activation_url,
    })
    send_mail('Activate your UCA Marketplace account', message, None, [user.email])


def register(request):
    if request.user.is_authenticated:
        return redirect('listings:index')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            send_activation_email(request, user)
            messages.success(
                request,
                f'Almost done, {user.username}! We sent an activation link to {user.email}. '
                'Open it to activate your account, then log in.',
            )
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})


def activate(request, uidb64, token):
    try:
        user = User.objects.get(pk=force_str(urlsafe_base64_decode(uidb64)))
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save(update_fields=['is_active'])
        # Logging in updates last_login, which also makes this link stop working.
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        messages.success(request, 'Your account is active. Welcome to UCA Marketplace!')
        return redirect('listings:index')

    messages.error(request, 'This activation link is invalid or has already been used.')
    return redirect('login')


@login_required
def profilepage(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)

    my_listings = request.user.listings.all()
    return render(request, 'users/profile.html', {'form': form, 'my_listings': my_listings})
