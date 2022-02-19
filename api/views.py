from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from api.wallet_serializer import KhaltiCallbackSerializer
from csgo import models as csgo_models
from . import serializers
from .permissions import IsOwnerOrReadOnly
from rest_framework.response import Response
from csgo.api_parsers.steam_inventory import Inventory
from django.contrib.auth import get_user_model
from csgo import filters as csgo_filters

from csgo.logic import khalti


USER_MODEL = get_user_model()


class ListingViewSet(ModelViewSet):
    queryset = csgo_models.Listing.objects.all().select_related('owner', 'inventory',
                                                    'inventory__item').prefetch_related('inventory__addons', 'inventory__addons__item')
    serializer_class = serializers.ListingListSerializer
    serializer_classes = {'list': serializers.ListingListSerializer,
                          'create': serializers.ListingCreateSerializer,
                          'update': serializers.ListingUpdateSerializer,
                          'partial_update': serializers.ListingUpdateSerializer,
                          }
    permission_classes = [IsOwnerOrReadOnly]
    pagination = True
    filterset_class = csgo_filters.ListingFilter

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.serializer_class)

    def get_serializer(self, *args, **kwargs):
        if self.action == 'create':
            kwargs['many'] = True
        return super().get_serializer(*args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class CartItemViewSet(ModelViewSet):
    queryset = csgo_models.CartItem.objects.all()
    serializer_class = serializers.CartItemSerializer
    serializer_classes = {'list': serializers.CartItemListSerializer}
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    pagination_class = None

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.serializer_class)

    def get_queryset(self):
        user = self.request.user
        return csgo_models.CartItem.objects.filter(owner=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(methods=['GET'],detail=False)
    def count(self,request):
        user = self.request.user
        length = csgo_models.CartItem.objects.filter(owner=user).count()
        return Response({'length':length})

class InventoryItemViewSet(ReadOnlyModelViewSet):
    queryset = csgo_models.InventoryItem.objects.filter(item_state=csgo_models.InventoryItem.ItemStateChoices.INV).select_related(
        'owner', 'item').prefetch_related('addons', 'addons__item')
    serializer_class = serializers.InventoryItemListSerializer
    permission_classes = []

    @action(detail=False, methods=['GET'], permission_classes=[IsAuthenticated])
    def my_inventory(self, request):
        user = request.user
        query = csgo_models.InventoryItem.objects.filter(owner=user, item_state=csgo_models.InventoryItem.ItemStateChoices.INV).select_related(
            'item', 'owner').prefetch_related('addons', 'addons__item')
        serializer = serializers.InventoryItemListSerializer(query, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'], permission_classes=[IsAuthenticated])
    def update_inventory(self, request):
        user = request.user
        inv = Inventory(user)
        inv.update_inventory()
        return Response(status=200)


class WalletTransactionViewSet(ModelViewSet):
    queryset = csgo_models.WalletTransaction.objects.all()
    serializer_class = serializers.WalletTransactionSerializer
    permission_classes = [IsAuthenticated,IsOwnerOrReadOnly]

    @action(detail=False, methods=['POST'])
    def load_funds(self, request):
        user = request.user
        serializer = KhaltiCallbackSerializer(data=request.data)
        resp = khalti.verify_khalti(serializer.data)
        if resp.get('success'):
            data = resp.get('data')
            khalti_txn = csgo_models.KhaltiTransaction.objects.create(
                idx=data.get('idx'), amount=data.get('amount'))
            csgo_models.WalletTransaction.objects.create(owner=user, amount=resp.get(
                'amount'), type=csgo_models.WalletTransaction.TypeChoice.CR, khalti=khalti_txn)
            # Add funds to the user
            user.add_credit(data.get('amount'))
            return Response(status=200)
        else:
            return Response(status=400)

    @action(detail=False, methods=['post'])
    def withdraw_funds(self, request):
        return Response(status=200)


class TransactionViewSet(ModelViewSet):
    queryset = csgo_models.Transaction.objects.all()
    serializer_class = serializers.TransactionSerializer
    permission_classes = []


class KhaltiTransactionViewSet(ModelViewSet):
    queryset = csgo_models.KhaltiTransaction.objects.all()
    serializer_class = serializers.KhaltiTransactionSerializer
    permission_classes = []
