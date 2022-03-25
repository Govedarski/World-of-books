from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from my_project.accounts.views import RegisterUserView, DoneRegistrationView, LoginUserView, LogoutUserView, \
    MyResetPasswordView, MyPasswordResetDoneView, MyPasswordResetConfirmView, MyPasswordResetCompleteView, \
    MyPasswordChangeView, AccountDetailsView

urlpatterns = [
    path('registration/', RegisterUserView.as_view(), name='create_user'),
    path('registration/done', DoneRegistrationView.as_view(), name='done_registration'),
    path('login/', LoginUserView.as_view(), name='login_user'),
    path('logout/', LogoutUserView.as_view(), name='logout_user'),

    path('reset_password/', MyResetPasswordView.as_view(), name='password_reset'),
    path('reset_password/done/', MyPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>', MyPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset_complited/', MyPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('change_password/', MyPasswordChangeView.as_view(), name='change_password'),

    path('', include('allauth.urls')),

    path('details/', AccountDetailsView.as_view(), name = 'show_account_details')
]
