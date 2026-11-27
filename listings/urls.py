from django.urls import path

from . import views

app_name = 'listings'

urlpatterns = [
    path('', views.ListingListView.as_view(), name='index'),
    path('new/', views.ListingCreateView.as_view(), name='create'),
    path('<int:pk>/', views.ListingDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.ListingUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.ListingDeleteView.as_view(), name='delete'),
    path('<int:pk>/status/', views.update_status, name='update_status'),
]
