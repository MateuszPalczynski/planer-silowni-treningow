from django.urls import path
from .views import user_login, register, home
# import for logout
from django.contrib.auth.views import LogoutView
from django.conf.urls.static import static

urlpatterns = [
    path('', home, name='home'),
    path('login/', user_login, name='login'),
    path('register/', register, name='register'),
    # path for logout
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
]
