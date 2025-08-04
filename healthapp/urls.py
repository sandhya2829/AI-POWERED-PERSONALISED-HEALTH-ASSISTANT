from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('predict/', views.predict_view, name='predict'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('diet/', views.diet_plan_view, name='diet'),
    path('workout/', views.workout_plan_view, name='workout'),
    path('exercise-search/', views.exercise_search_view, name='exercise_search'),
    path('diet-search/', views.diet_search_view, name='diet_search'),
    path('progress/', views.progress_view, name='progress'),
    path('health-history/', views.health_history_view, name='health_history'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
