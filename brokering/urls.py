from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StockList, TransactionViewSet, HoldingViewSet

router = DefaultRouter()
router.register('stocks', StockList, basename='stock')
router.register('transactions', TransactionViewSet, basename='transaction')
# router.register('holdings', HoldingViewSet, basename='holding')

urlpatterns = [
    path('', include(router.urls)),
    path('holdings/', HoldingViewSet.as_view())
]