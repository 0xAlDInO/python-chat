from django.core.management.base import BaseCommand
from chat_app.models import Room, User

class Command(BaseCommand):
    help = 'Crée les tables et initialise les données utilisateurs et salles de test par défaut.'

    def handle(self, *args, **options):
        # Create Rooms
        r_gen, _ = Room.objects.get_or_create(id="101", defaults={'name': "Salon Général", 'description': "Espace général des collaborateurs"})
        r_dev, _ = Room.objects.get_or_create(id="dev", defaults={'name': "Salle Développement", 'description': "Équipe technique et ingénierie"})
        r_reu, _ = Room.objects.get_or_create(id="reunion", defaults={'name': "Salle Réunion", 'description': "Espace de briefing et réunions"})
        r_dir, _ = Room.objects.get_or_create(id="directeur", defaults={'name': "Salle Direction", 'description': "Comité de direction Oxalix"})

        # Users and authorizations
        users_data = [
            ("OX-001", "Alice", "Dupont", "Chef de Projet", [r_gen, r_dev, r_reu]),
            ("OX-002", "Jean", "Martin", "Développeur Senior", [r_gen, r_dev]),
            ("OX-003", "Sophie", "Bernard", "UI/UX Designer", [r_gen, r_reu]),
            ("OX-004", "Thomas", "Dubois", "Ingénieur DevOps", [r_gen, r_dev]),
            ("OX-005", "Claire", "Moreau", "Directrice Générale", [r_gen, r_dev, r_reu, r_dir]),
        ]

        for u_id, prenom, nom, fonction, rooms in users_data:
            user, created = User.objects.get_or_create(
                id=u_id,
                defaults={'prenom': prenom, 'nom': nom, 'fonction': fonction}
            )
            user.authorized_rooms.set(rooms)
            user.save()

        self.stdout.write(self.style.SUCCESS("Base de données initialisée avec succès ! Les utilisateurs et leurs autorisations :"))
        for u in User.objects.all():
            rooms_list = ", ".join([f"{r.name} ({r.id})" for r in u.authorized_rooms.all()])
            self.stdout.write(f"  - {u.id}: {u.prenom} {u.nom} ({u.fonction}) -> Salles: [{rooms_list}]")
