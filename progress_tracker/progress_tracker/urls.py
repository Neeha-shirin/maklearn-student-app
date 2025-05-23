
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from learning import views as learning_views

urlpatterns = [
    path('admin/', admin.site.urls),

    
    # Include learning app URLs (like dashboard, login, etc)
    path('', include('learning.urls')),
     path('staff/', include('staff.urls')),
     path('staff/', lambda request: redirect('staff_login')),  # ✅ This line
    path('review/', include('review.urls')),
   
]
