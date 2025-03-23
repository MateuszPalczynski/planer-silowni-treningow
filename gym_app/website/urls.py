from django.urls import path
from .views import user_login, register, home
from django.conf.urls.static import static

urlpatterns = [
    path('', home, name='home'),
    path('login/', user_login, name='login'),
    path('register/', register, name='register'),
]
