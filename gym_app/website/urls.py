from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import (
    user_login, register, home, create_training_plan, edit_training_plan, 
    delete_training_plan, update_training_plan, update_trainer_notes, 
    mark_training_plan_done, training_history, training_history_detail
)

urlpatterns = [
    path('', home, name='home'),
    path('login/', user_login, name='login'),
    path('register/', register, name='register'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('create_training_plan/', create_training_plan, name='create_training_plan'),
    path('edit_training_plan/<int:pk>/', edit_training_plan, name='edit_training_plan'),
    path('delete-plan/<int:pk>/', delete_training_plan, name='delete_training_plan'),
    path('training/update/<int:pk>/', update_training_plan, name='update_training_plan'),
    path('training/update_trainer_notes/<int:pk>/', update_trainer_notes, name='update_trainer_notes'),
    path('training/mark_done/<int:plan_id>/', mark_training_plan_done, name='mark_training_plan_done'),
    path('training/history/', training_history, name='training_history'),
    path('training/history/<int:completion_id>/', training_history_detail, name='training_history_detail'),
]
