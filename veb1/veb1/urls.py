# veb1/urls.py
# --- (Inside your project's urls.py - veb1/veb1/urls.py) ---

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('blog/', include('blog.urls')),  # Include your app's urls
]