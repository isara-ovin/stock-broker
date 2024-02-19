import factory
from factory import fuzzy
from datetime import datetime
from factory.django import DjangoModelFactory
from django.contrib.auth.models import User
from brokering.models import Stock, StockPrice, Transaction

class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: 'user%d' % n)

class StockFactory(DjangoModelFactory):
    class Meta:
        model = Stock

    name = factory.Sequence(lambda n: 'Stock %d' % n)
    description = 'Test description'

class StockPriceFactory(DjangoModelFactory):
    class Meta:
        model = StockPrice

    stock = factory.SubFactory(StockFactory)
    price = fuzzy.FuzzyFloat(1.00, 100.00)
    count = fuzzy.FuzzyInteger(1, 100)

class TransactionFactory(DjangoModelFactory):
    class Meta:
        model = Transaction

    user = factory.SubFactory(UserFactory)
    stock = factory.SubFactory(StockFactory)
    transaction_type = 'BUY'
    quantity = 10
    price_per_unit = 100.0
    total_price = 1000.0
    timestamp = datetime.now().isoformat()
