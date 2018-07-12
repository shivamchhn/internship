from django.urls import path
from . import views
from django.conf import settings
from django.contrib.auth.views import (
    login, logout,
    password_reset, password_reset_done,
    password_reset_confirm, password_reset_complete
)
from django.shortcuts import reverse

app_name = 'accounts'
urlpatterns = [
path('', views.home, name="home"),
    path('aftersignup/', views.after_register, name="after_register"),
    path('login/', login, {'template_name': 'accounts/login.html'}, name='login'),
    path('logout/', logout, {'template_name': 'accounts/logout.html'}, name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.view_profile, name='view_profile'),
    path('profile/<int:pk>', views.view_profile, name='view_profile_with_pk'),
    path('profile_edit', views.update_profile, name='edit_profile'),
    path('change-password/', views.change_password, name='change_password'),
    path('reset-password/', password_reset, {'template_name': 'accounts/reset_password.html',
                                             'email_template_name': 'accounts/reset_password_mail.html',
                                             'from_email': settings.EMAIL_HOST,
                                             'post_reset_redirect':
                                                 'accounts:password_reset_done'}, name='reset_password'),
    path('reset-password/done/', password_reset_done, {'template_name': 'accounts/reset_password_done.html'}, name='password_reset_done'),
    path('reset-password/confirm/<uidb64>/<token>/', password_reset_confirm, {'template_name': 'accounts/password_reset_confirm.html'}, name='password_reset_confirm'),


]
