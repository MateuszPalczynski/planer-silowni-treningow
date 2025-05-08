from django.urls import path

from django.contrib.auth.views import LogoutView
from .views import user_login, register, home, create_training_plan
from django.conf.urls.static import static

urlpatterns = [
    path('', home, name='home'),
    path('login/', user_login, name='login'),
    path('register/', register, name='register'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('create_training_plan/', create_training_plan, name='create_training_plan'),
]

