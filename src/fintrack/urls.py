from django.urls import path
from .views import landing_page
from . import views

from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('records/add/', views.add_record_view, name='add_record'),
    path('summary/', views.summary_view, name='summary'),
    path('budget/', views.budget_view, name='budget'),
    path('edit/<int:record_id>/', views.edit_record_view, name='edit_record'),
    path('delete/<int:record_id>/', views.delete_record_view, name='delete_record'),
]
