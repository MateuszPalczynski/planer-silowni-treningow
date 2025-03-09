from django.urls import path
from .views import LoginPageView, register, home
from django.conf.urls.static import static

urlpatterns = [
    path('', home, name='home'),
    path('login/', LoginPageView.as_view(), name='login'),
    path('register/', register, name='register'),
]
