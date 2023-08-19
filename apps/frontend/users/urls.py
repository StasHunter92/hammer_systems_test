from django.urls import path

from apps.frontend.users import views

# ----------------------------------------------------------------------------------------------------------------------
# Create urls
urlpatterns = [
    path('', views.UserSignupLoginView.as_view(), name='user-identify'),
    path('authenticate/', views.UserAuthenticationView.as_view(), name='user-authenticate'),
    path('profile/', views.UserRetrieveView.as_view(), name='user-profile'),
    path('profile/logout/', views.UserLogoutView.as_view(), name='user-logout'),
    path('profile/submit/', views.UserConfirmInviteView.as_view(), name='user-submit'),
]
