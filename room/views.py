from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .forms import RoomForm
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Room, Message
from core.models import Profile


@login_required
def rooms(request):
    rooms = Room.objects.all()
    profiles = Profile.objects.all()  # Получаем всех пользователей
    print(profiles)
    context = {
        'rooms': rooms,
        'profiles': profiles,  # Передаем список всех пользователей в контекст
    }
    return render(request, 'room/rooms.html', {'rooms': rooms})

@login_required
def room(request, id):
    room = Room.objects.get(id=id)
    messages = Message.objects.filter(room=room)

    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Message.objects.create(room=room, user=request.user, content=content)
            return redirect('room', id=id)  # Перенаправляем обратно на страницу чата

    return render(request, 'room/room.html', {'room': room, 'messages': messages})


def create_room(request):
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('rooms')  # Перенаправляем на страницу с комнатами после создания
    else:
        form = RoomForm()
    return render(request, 'room/room_create.html', {'form': form})

@login_required
def send_message(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            room_id = request.POST.get('room_id')  # Предполагается, что в форме будет поле room_id, указывающее на текущую комнату
            room = Room.objects.get(id=room_id)
            Message.objects.create(room=room, user=request.user, content=content)
    return redirect('room', id=room.id)


def room_edit(request, room_id):
    room = get_object_or_404(Room, id=room_id)

    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('rooms')  # Замените на ваше представление списка комнат
    else:
        form = RoomForm(instance=room)

    return render(request, 'room/room_edit.html', {'form': form})

def room_delete(request, room_id):
    room = get_object_or_404(Room, id=room_id)

    if request.method == 'POST':
        room.delete()
        return redirect('rooms')  # Замените на ваше представление списка комнат

    return render(request, 'room/room_delete.html', {'room': room})