from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView

# ----------------------------------------------------------------------------------------------------------------------
# Create urls
urlpatterns = [
    path('users/', include('apps.api.v1.users.urls')),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
