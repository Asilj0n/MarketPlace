from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from users import views as user_views
from users.forms import LoginForm

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('listings.urls')),
    path('register/', user_views.register, name='register'),
    path('activate/<uidb64>/<token>/', user_views.activate, name='activate'),
    path('login/', auth_views.LoginView.as_view(
        template_name='users/login.html',
        authentication_form=LoginForm,
        redirect_authenticated_user=True,
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', user_views.profilepage, name='profile'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
