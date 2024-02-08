from rest_framework import generics
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAdminOrReadOnly, IsInvestorOrReadOnly
from .models import Stock, StockPrice, Transaction, Holding
from .serializers import StockSerializer, StockPriceSerializer, TransactionSerializer, HoldingSerializer
from .filters import StockModelFilter


class StockList(ModelViewSet): # ModelViewSet
    queryset = Stock.objects.prefetch_related('price_history')
    serializer_class = StockSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = StockModelFilter
    permission_classes = [IsAdminOrReadOnly]  # Only authenticated users can access


class TransactionViewSet(ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated, IsInvestorOrReadOnly]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class HoldingViewSet(generics.ListAPIView):
    queryset = Holding.objects.all()
    serializer_class = HoldingSerializer
    permission_classes = [IsAuthenticated, IsInvestorOrReadOnly]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
