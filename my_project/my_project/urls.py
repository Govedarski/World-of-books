"""my_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from my_project.common.helpers.custom_wrapers import staff_required

admin.site.login = staff_required(admin.site.login)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('my_project.common.urls')),
    path('accounts/', include('my_project.accounts.urls')),
    path('books/', include('my_project.library.urls')),
    path('offers/', include('my_project.offer.urls')),
]
urlpatterns += static(settings.MEDIA_URL,
                      document_root=settings.MEDIA_ROOT)

admin.site.index_title = 'The world of books'
admin.site.site_header = ' Admin: The world of books'
admin.site.site_title = 'Admin'

urlpatterns += staticfiles_urlpatterns()