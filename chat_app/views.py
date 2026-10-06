import os
import time
from datetime import datetime
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.utils.text import slugify
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import User, Room, Message

def home(request):
    error = request.GET.get('error')
    return render(request, "index.html", {'error': error})

def get_user_rooms(request, user_id):
    try:
        user = User.objects.get(id=user_id.strip().upper())
        return JsonResponse({
            'valid': True,
            'authorized_rooms': [r.to_dict() for r in user.authorized_rooms.all()]
        })
    except User.DoesNotExist:
        return JsonResponse({'valid': False, 'error': 'ID Utilisateur inexistant'}, status=404)

def chat(request):
    user_id = request.GET.get('user_id', '').strip().upper()
    room_id = request.GET.get('room', '').strip().lower()

    if not user_id or not room_id:
        return redirect('/?error=' + 'Veuillez renseigner votre ID et la salle de discussion.')

    # 1. Check user
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return redirect('/?error=' + f"Identifiant '{user_id}' inexistant dans la base Back-Office.")

    # 2. Check room
    room = Room.objects.filter(id=room_id).first()
    if not room:
        room = Room.objects.filter(name__iexact=room_id).first()

    if not room:
        return redirect('/?error=' + f"La salle '{room_id}' n'existe pas.")

    # 3. Check authorization
    if room not in user.authorized_rooms.all():
        return redirect('/?error=' + f"Accès refusé : L'identifiant {user.id} n'a pas l'autorisation pour la {room.name} ({room.id}).")

    return render(
        request,
        'chat.html',
        {
            'user_id': user.id,
            'username': f"{user.prenom} {user.nom}",
            'fonction': user.fonction,
            'room': room.id,
            'room_name': room.name,
            'user_authorized_rooms': [r.to_dict() for r in user.authorized_rooms.all()]
        }
    )

@csrf_exempt
def upload_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
        filename = f"{int(datetime.utcnow().timestamp())}_{uploaded_file.name}"
        save_path = os.path.join(settings.MEDIA_ROOT, filename)

        with open(save_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        file_url = f"/static/uploads/{filename}"
        ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
        file_type = 'image' if ext in ['png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'] else 'file'

        return JsonResponse({
            'file_url': file_url,
            'filename': uploaded_file.name,
            'file_type': file_type
        })
    return JsonResponse({'error': 'Aucun fichier sélectionné'}, status=400)

def get_room_history(request, room):
    messages = Message.objects.filter(room=str(room)).order_by('timestamp')
    return JsonResponse([msg.to_dict() for msg in messages], safe=False)
