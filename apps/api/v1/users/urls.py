from django.urls import path

from apps.api.v1.users import views

# from apps.users import views
# ----------------------------------------------------------------------------------------------------------------------
# Create urls
urlpatterns = [
    path('login', views.UserSignupLoginView.as_view(), name='user-login'),
    path('authenticate', views.UserAuthenticationView.as_view(), name='user-authenticate'),
    path('profile', views.UserRetrieveView.as_view(), name='user-profile'),
]
