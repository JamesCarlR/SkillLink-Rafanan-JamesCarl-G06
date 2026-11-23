from django.urls import path
from . import views

urlpatterns = [
    path('', views.SkillListView.as_view(), name='skill-list'),
    path('new/', views.SkillCreateView.as_view(), name='skill-create'),
    path('<int:pk>/edit/', views.SkillUpdateView.as_view(), name='skill-update'),
    path('<int:pk>/delete/', views.SkillDeleteView.as_view(), name='skill-delete'),
]