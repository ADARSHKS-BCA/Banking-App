"""
URL configuration for BankManagement project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# ========== MAIN URL PATTERNS ==========
# This is the root URL configuration for the entire project
# It includes URLs from individual apps
urlpatterns = [
    # Admin panel URL (hidden from users, only accessible via direct URL)
    # Example: http://127.0.0.1:8000/admin/
    path('admin/', admin.site.urls),
    
    # Include all URLs from accounts app
    # Empty string means these URLs are at the root level
    # Example: http://127.0.0.1:8000/ (home page)
    path('', include('accounts.urls')),
    
    # Include all URLs from transactions app
    # Prefixed with 'transactions/'
    # Example: http://127.0.0.1:8000/transactions/deposit/
    path('transactions/', include('transactions.urls')),
]

# ========== STATIC AND MEDIA FILES (Development Only) ==========
# These settings are only active when DEBUG=True (development mode)
# In production, static files should be served by the web server (nginx, Apache)
if settings.DEBUG:
    # Serve media files (user uploads) during development
    # Example: http://127.0.0.1:8000/media/image.jpg
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Serve static files (CSS, JavaScript, images) during development
    # Example: http://127.0.0.1:8000/static/css/style.css
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
