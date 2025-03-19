from django.urls import path
from . import views

app_name = 'dispatch'

urlpatterns = [
    path('', views.DispatchListView.as_view(), name='dispatch_list'),
    path('<int:pk>/', views.DispatchDetailView.as_view(), name='dispatch_detail'),
    path('add/', views.add_or_edit_dispatch, name='dispatch_add'),
    path('<int:pk>/edit/', views.add_or_edit_dispatch, name='dispatch_edit'),
    path('<int:pk>/delete/', views.delete_dispatch, name='dispatch_delete'),
    path('<int:pk>/status/<str:status>/', views.update_dispatch_status, name='update_status'),
]
