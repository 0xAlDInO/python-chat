from django.contrib import admin
from .models import Room, User, Message

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')
    search_fields = ('id', 'name')

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'prenom', 'nom', 'fonction', 'get_authorized_rooms')
    search_fields = ('id', 'prenom', 'nom', 'fonction')
    filter_horizontal = ('authorized_rooms',)

    def get_authorized_rooms(self, obj):
        return ", ".join([r.id for r in obj.authorized_rooms.all()])
    get_authorized_rooms.short_description = 'Salles Autorisées'

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'room', 'username', 'message', 'timestamp')
    list_filter = ('room', 'timestamp')
    search_fields = ('username', 'message', 'room')
