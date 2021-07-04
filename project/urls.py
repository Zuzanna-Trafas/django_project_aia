
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from . import views

urlpatterns = [
    path('accounts/home/', views.main, name='main'),
    path('admin/', admin.site.urls),
    path('details/<int:tournament_id>', views.details, name='details'),
    path('add/', views.add, name='add'),
    path('my_events/', views.my_events, name='my_events'),
    path('apply/<int:tournament_id>', views.apply, name='apply'),
    path('edit/<int:tournament_id>', views.edit, name='edit'),
    url(r'^$', views.index, name='home'),
    path('accounts/', include('django.contrib.auth.urls')),
    url(r'^accounts/sign_up/$', views.signup, name='signup'),
    path('activate/<uidb64>/<token>/',
         views.activate, name='activate'),
    url('^', include('django.contrib.auth.urls')),
]
