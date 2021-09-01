from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser,IsAuthenticated
from rest_framework.response import Response
from rest_framework import generics,status
from rest_framework.viewsets import ModelViewSet
from .serializers import ItemSerializer, ListingSerializer,AddonSerializer,ListingList

from .models import Item, Listing
from .permissions import IsOwnerOrReadOnly,ReadOnly

# class CsgoitemsList(APIView):

#     def get(self,request):
#         queryset = Listing.objects.all()
#         serializer = ListingList(queryset,many=True)
#         return Response(serializer.data)

#     def post(self, request):
#         if not request.user.is_authenticated:
#             return Response(status=status.HTTP_401_UNAUTHORIZED)

#         serializer = ListingSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save(owner=request.user)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ItemViewSet(ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [IsAdminUser|ReadOnly]

class ListingViewSet(ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.validated_data['owner'] = self.request.user
        return super(ListingViewSet, self).perform_create(serializer)



class CsgoitemsDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated,IsOwnerOrReadOnly]
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer


class CsgoaddonDetail(APIView):
    
    def post(self,request):
        serializer = AddonSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
