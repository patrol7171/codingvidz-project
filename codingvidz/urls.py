"""codingvidz URL Configuration
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from groups import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('dashboard', views.dashboard, name='dashboard'),
    # AUTH
    path('signup', views.SignUp.as_view(), name='signup'),
    path('login', auth_views.LoginView.as_view(), name='login'),
    path('logout', auth_views.LogoutView.as_view(), name='logout'),
    # Group
    path('vidzgroup/create', views.CreateGroup.as_view(), name='create_group'),
    path('vidzgroup/<int:pk>', views.DetailGroup.as_view(), name='detail_group'),
    path('vidzgroup/<int:pk>/update', views.UpdateGroup.as_view(), name='update_group'),
    path('vidzgroup/<int:pk>/delete', views.DeleteGroup.as_view(), name='delete_group'),
    # Video
    path('vidzgroup/<int:pk>/addvideo', views.add_video, name='add_video'),
    path('video/search', views.video_search, name='video_search'),
    path('video/<int:pk>/delete', views.DeleteVideo.as_view(), name='delete_video'),
] 
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
