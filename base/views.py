from django.shortcuts import render, redirect
from django.db.models import Q, Count
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .models import Room, Topic, Message,User
from .forms import RoomForm, UserForm,MyUserCreationForm


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
        email = request.POST.get("email").lower()
        password = request.POST.get("password")
        
        # TODO: check if user exists in database
        try:
            user = User.objects.get(email = email)
        except:
            messages.error(request, "user dose not exist !")
            
        # TODO: return user if correct information else return None
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "username/email OR password dose not exist !")

    context ={'page':page}
    return render(request, "base/login_register.html", context)


def logoutUser(request):
    #  remove session ID from cookie to logout
    logout(request)
    return redirect("home")

def registerPage(request):
    form = MyUserCreationForm()   
    if request.method == "POST":
        form = MyUserCreationForm(request.POST)
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
    
    # rooms = Room.objects.filter(
    #     Q(topic__name__icontains = q) |
    #     Q(name__icontains = q) |
    #     Q(desription__icontains = q) 
        
        
    #     )
    rooms = Room.objects.filter(
        Q(topic__name__iexact = q) |
        Q(name__iexact = q) |
        Q(desription__iexact = q) 
        
        )
    
    # Get the topics and annotate them with the count of related rooms
    topics = Topic.objects.annotate(room_count=Count('room'))

    # Order the topics by the count of related rooms in descending order
    topics = topics.order_by('-room_count')[:3]  # Get the top 3 topics
    
    # topics = Topic.objects.all()[0:4] #  limit only get 3 topics of all topic
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains = q))
    # room_messages = Message.objects.filter(room__topic__name__iexact=q)

    
    
    
    context = {"rooms":rooms,
               "topics":topics,
               "room_count": room_count, 
               "room_messages": room_messages}
    return render(request, "base/home.html", context)

def room(request, pk): # request mean that: maybe it is GET method or POST
    
    room = Room.objects.get(id = pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()
    
    
    if request.method == 'POST':
        
        
        message = Message.objects.create(
            user  = request.user,
            room = room,
            body = request.POST.get("body")
        )
        room.participants.add(request.user)
        return redirect("room", pk = room.id)
    
    context = {"room":room, "room_messages":room_messages, "participants":participants}
    
    
    return render(request, "base/room.html", context)


def userProfile(request, pk):
    
    user = User.objects.get(id = pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    
    context = {"user": user, 
               "rooms": rooms, 
               "room_messages": room_messages,
               "topics": topics
               }
    return render(request, "base/profile.html",context)

@login_required(login_url = 'login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    
    if request.method == "POST":
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host = request.user,
            topic = topic,
            name = request.POST.get("name"),
            desription = request.POST.get("desription")
        ) 
        return redirect("home")
    
    context = {"form": form, 'topics': topics}
    return render(request, "base/room_form.html",context) 


@login_required(login_url = 'login')
def updateRoom(request, pk):
    room = Room.objects.get(id = pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    if request.user != room.host :
        return HttpResponse("You do not have permission to do that ")
    
    if request.method == "POST":
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.desription = request.POST.get('desription')
        room.save()
      
        return redirect("home")
    
    context = {"form":form, "topics":topics, 'room':room}
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
    
    
@login_required(login_url = 'login')
def deleteMessage(request, pk):
    message = Message.objects.get(id = pk)
    
    if request.user != message.user :
        return HttpResponse("You do not have permission to do that ")
    
    if request.method == "POST":
        message.delete()
        return redirect("home")
    
    return  render(request, "base/delete.html", {"obj": message})
    

@login_required(login_url="login")
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == "POST":
        form = UserForm(request.POST,request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect("user-profile", pk=user.id)

            
    context = {'form':form}
    return render(request, "base/update-user.html", context)

def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    topics = Topic.objects.filter(name__icontains=q)
    context = {"topics": topics}
    return render(request, "base/topics.html", context)

def activityPage(request):
    
    room_messages = Message.objects.all()

    context = {'room_messages': room_messages}

    return render(request, "base/activity.html", context)
    