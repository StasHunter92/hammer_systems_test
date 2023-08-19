from django.urls import path, include

# ----------------------------------------------------------------------------------------------------------------------
# Create urls
urlpatterns = [
    path('v1/', include('apps.api.v1.urls')),
]
