from django.urls import path
from . import views

urlpatterns = [
    path('', views.student_dashboard, name='student_dashboard'),
    path('complete-task/<int:task_id>/', views.complete_task, name='complete_task'),
    
    path('submit-review/', views.submit_review, name='submit_review'),
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    
    
    

]
