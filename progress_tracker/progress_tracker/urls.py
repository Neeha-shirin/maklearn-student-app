
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from learning import views as learning_views
from app1 import views as app1_views 
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),

     path('', app1_views.home, name='home'),

    path('learning', include('learning.urls')),
     path('staff/', include('staff.urls')),
     path('staff/', lambda request: redirect('staff_login')),  # ✅ This line
    path('review/', include('review.urls')),
    path('app1/',include('app1.urls'))
   
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
