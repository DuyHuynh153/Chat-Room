from rest_framework.decorators import api_view
from rest_framework.response import Response
from base.models import Room
from .serializers import RoomSerializer

@api_view(['GET'])
def getRoutes(request):
    routes = [
        'GET /api/',
        'GET /api/rooms',
        'GET /api/rooms/:id',
        
    ]
    return Response(routes)
    
    
@api_view(['GET'])
def getRooms(request):
    rooms = Room.objects.all()
    serialzier = RoomSerializer(rooms, many = True)  #  many mean that there are more than one object convert into JSON
    
    return Response(serialzier.data)

@api_view(['GET'])
def getRoom(request,pk):
    room = Room.objects.get(id=pk)
    serialzier = RoomSerializer(room, many = False)  #  many mean that there are more than one object convert into JSON
    
    return Response(serialzier.data)