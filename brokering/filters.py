import django_filters
from .models import Stock

class StockModelFilter(django_filters.FilterSet):
    
    class Meta:
        model = Stock
        fields = {
            'name': ['exact', 'icontains'],
        }
