from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from csgo.models import Item,Listing

from .serializers import ItemSerializer, ListingSerializer, ListingNestedSerializer
from .permissions import IsOwnerOrReadOnly,ReadOnly


class ItemViewSet(ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [IsAdminUser|ReadOnly]

class ListingViewSet(ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def list(self, request):
        queryset = self.queryset
        serializer = ListingNestedSerializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.validated_data['owner'] = self.request.user
        return super(ListingViewSet, self).perform_create(serializer)