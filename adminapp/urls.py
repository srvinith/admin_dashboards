from django.urls import path
from .import views
urlpatterns=[
path ('',views.home,name="home"),
path('flead/',views.flead),
path('get_data/',views.get_data),
]