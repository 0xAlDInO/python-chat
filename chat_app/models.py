from django.db import models

class Room(models.Model):
    id = models.CharField(max_length=50, primary_key=True) # e.g. "dev", "reunion", "directeur", "101"
    name = models.CharField(max_length=100) # e.g. "Salle Développement"
    description = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.id})"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description or ''
        }

class User(models.Model):
    id = models.CharField(max_length=50, primary_key=True) # e.g. "OX-001"
    nom = models.CharField(max_length=80)
    prenom = models.CharField(max_length=80)
    fonction = models.CharField(max_length=100)
    authorized_rooms = models.ManyToManyField(Room, related_name='authorized_users', blank=True)

    def __str__(self):
        return f"{self.id} - {self.prenom} {self.nom} ({self.fonction})"

    def to_dict(self):
        return {
            'id': self.id,
            'nom': self.nom,
            'prenom': self.prenom,
            'full_name': f"{self.prenom} {self.nom}",
            'fonction': self.fonction,
            'authorized_rooms': [r.to_dict() for r in self.authorized_rooms.all()]
        }

class Message(models.Model):
    username = models.CharField(max_length=80)
    room = models.CharField(max_length=50)
    message = models.TextField()
    file_url = models.CharField(max_length=255, blank=True, null=True)
    file_type = models.CharField(max_length=20, blank=True, null=True) # 'image' or 'file'
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"[{self.room}] {self.username}: {self.message[:30]}"

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'room': self.room,
            'message': self.message,
            'file_url': self.file_url,
            'file_type': self.file_type,
            'timestamp': self.timestamp.strftime('%H:%M')
        }
