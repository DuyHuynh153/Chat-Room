from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Room, Topic, Message
from .forms import RoomForm


# Create your views here.

# rooms = [
#     {"id":1, "name": "huynh lam duy"},
#     {"id":2, "name": "just kidding"},
#     {"id":3, "name": "hihi nhahaha hoho"},
#     {"id":4, "name": "kasjdljasljasdjlk"},
    
    
# ]

def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect("home")
    
    if request.method == "POST":
        username = request.POST.get("username").lower()
        password = request.POST.get("password")
        
        # TODO: check if user exists in database
        try:
            user = User.objects.get(username = username)
        except:
            messages.error(request, "user dose not exist !")
            
        # TODO: return user if correct information else return None
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "username OR password dose not exist !")

    context ={'page':page}
    return render(request, "base/login_register.html", context)


def logoutUser(request):
    #  remove session ID from cookie to logout
    logout(request)
    return redirect("home")

def registerPage(request):
    form = UserCreationForm()   
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect("home")
        
        else:
            messages.error(request, "can not register user")            
    return render(request, 'base/login_register.html', {'form': form})

def home(request):  #  request mean that: maybe it is GET  method or POST method or something
    
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    
    rooms = Room.objects.filter(
        Q(topic__name__icontains = q) |
        Q(name__icontains = q) |
        Q(desription__icontains = q) 
        
        
        )
    
    topics = Topic.objects.all()
    room_count = rooms.count()
    
    
    context = {"rooms":rooms, "topics":topics, "room_count": room_count}
    return render(request, "base/home.html", context)

def room(request, pk): # request mean that: maybe it is GET method or POST
    
    room = Room.objects.get(id = pk)
    room_messages = room.message_set.all().order_by('-created')
    participants = room.participants.all()
    
    
    if request.method == 'POST':
        message = Message.objects.create(
            user  = request.user,
            room = room,
            body = request.POST.get("body")
        )
        return redirect("room", pk = room.id)
    
    context = {"room":room, "room_messages":room_messages, "participants":participants}
    
    
    return render(request, "base/room.html", context)

@login_required(login_url = 'login')
def createRoom(request):
    form = RoomForm()
    if request.method == "POST":
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("home")
    
    context = {"form": form}
    return render(request, "base/room_form.html",context) 


@login_required(login_url = 'login')
def updateRoom(request, pk):
    room = Room.objects.get(id = pk)
    form = RoomForm(instance=room)
    
    if request.user != room.host :
        return HttpResponse("You do not have permission to do that ")
    
    if request.method == "POST":
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect("home")
    
    context = {"form":form}
    return render(request, "base/room_form.html",context)


@login_required(login_url = 'login')
def deleteRoom(request, pk):
    room = Room.objects.get(id = pk)
    if request.user != room.host :
        return HttpResponse("You do not have permission to do that ")
    
    if request.method == "POST":
        room.delete()
        
        return redirect("home")
    
    return  render(request, "base/delete.html", {"obj": room})
    
    