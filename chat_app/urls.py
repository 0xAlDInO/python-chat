from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('chat', views.chat, name='chat'),
    path('upload', views.upload_file, name='upload'),
    path('api/user/rooms/<str:user_id>', views.get_user_rooms, name='user_rooms'),
    path('api/history/<str:room>', views.get_room_history, name='room_history'),
]
