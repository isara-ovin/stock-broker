import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from datetime import datetime

from django.contrib.auth.models import User
from brokering.models import Stock, Holding
from brokering.serializers import TransactionSerializer
from tests.factories import TransactionFactory, UserFactory, StockFactory, StockPriceFactory

@pytest.fixture
def api_client():
    # Create an API client
    client = APIClient()
    return client

@pytest.mark.django_db
class TestTransactions:   
    """ 
    Perform testing related to Transaction logic for Investors
        Coverage:
            201 Investor can buy existing stocks
                Records create or updates in Holdings
                Record increments its value when buying stock
            400 Investor can't buy non-existing stocks
            True non-existing detail error message
    """ 
    @pytest.fixture(autouse=True)
    def setup(self, api_client):
        # Create a investor, stock using pytest-factoryboy
        self.user = UserFactory.create(username='test_investor')
        self.stock = StockFactory()
        self.stock_dummy = StockFactory() # Creating invalid record for testing
        self.stock_price = StockPriceFactory(stock=self.stock, price=10, count=20)
        self.stock_price_dummy = StockPriceFactory(stock=self.stock_dummy, price=30, count=10)
        api_client.force_authenticate(user=self.user)

    # Investor has correct permissions
    def test_buy_existing_stock(self, api_client):
        url = '/api/brokering/transactions/'
        payload = {
                "transaction_type": "BUY",
                "quantity": 5,
                "price_per_unit": 10,
                "total_price": 50,
                "timestamp": datetime.now().isoformat(),
                "stock_name": self.stock.name}

        for _ in range(2):
            response = api_client.post(url, data=payload)

            # Transaction completed with validation and creation with Holdings
            assert response.status_code == 201


        # Correct record is inserted in Holdings table * 2
        holding_quantity = Holding.objects.get(user=self.user, stock=self.stock).quantity
        assert holding_quantity == payload['quantity'] * 2


    def test_buy_exceeding_stock(self, api_client):
        url = '/api/brokering/transactions/'
        payload = {
                "transaction_type": "BUY",
                "quantity": 500,
                "price_per_unit": 10,
                "total_price": 5000,
                "timestamp": datetime.now().isoformat(),
                "stock_name": self.stock.name}

        response = api_client.post(url, data=payload)
        data = response.json()

        # Validate status code
        assert response.status_code == 400

        # Validate error message with correct stock name and current stock count
        assert f'Not enough stocks from {self.stock.name} existing count is {self.stock_price.count}'  == data['detail'][0]


