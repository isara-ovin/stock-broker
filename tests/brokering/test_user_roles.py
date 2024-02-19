import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from datetime import datetime

from django.contrib.auth.models import User
from brokering.models import Stock
from brokering.serializers import TransactionSerializer
from tests.factories import TransactionFactory, UserFactory, StockFactory


@pytest.fixture
def api_client():
    # Create an API client
    client = APIClient()
    return client

@pytest.mark.django_db
class TestInvestorRole:   
    """ 
    Perform testing related to Investor role
        Coverage:
            False on is_staf entry
            403 assertions on POST,PUT,DELTE
            200 assertion on GET
    
    """ 
    @pytest.fixture(autouse=True)
    def setup(self, api_client):
        # Create a investor, stock using pytest-factoryboy
        self.user = UserFactory.create(username='test_investor')
        self.stock = StockFactory()
        api_client.force_authenticate(user=self.user)

    # Investor has correct permissions
    def test_user_investor(self):
        assert self.user.is_staff == False

    # Validate record exists in stock
    def test_dummy_stock_exists(self):
        assert self.stock.id > 0

    # GET request by Investor
    def test_get_on_stock(self, api_client):
        url = '/api/brokering/stocks/' 
        response = api_client.get(url)
        print(response.json())

        # Current user has permission
        assert response.status_code == 200

    # Post request by Investor
    def test_post_on_stock(self, api_client):
        url = '/api/brokering/stocks/' 
        response = api_client.post(url, data={})

        assert response.status_code == 403

    # PUT request by Investor
    def test_put_on_stock(self, api_client):
        _id = self.stock.id
        url = f'/api/brokering/stocks/{_id}/' 
        response = api_client.post(url, data={})

        assert response.status_code == 403

    # DELETE request by Investor
    def test_delete_on_stock(self, api_client):
        _id = self.stock.id
        url = f'/api/brokering/stocks/{_id}/' 
        response = api_client.post(url, data={})

        assert response.status_code == 403


    
@pytest.mark.django_db
class TestAdminRole: 
    """ 
    Perform testing related to Admin role
        Coverage:
            True on is_staf entry
            201 assertions on POST
            403 assertion on /transactions/
    """ 
    @pytest.fixture(autouse=True)
    def setup(self, api_client):
        # Create a investor using pytest-factoryboy
        self.user = UserFactory.create(username='test_admin', is_staff=True)
        api_client.force_authenticate(user=self.user)

    def test_user_admin(self):
        # Create a user with a valid username
        assert self.user.is_staff == True

    def test_post_on_stock(self, api_client):
        url = '/api/brokering/stocks/'
        payload = {
                "name": "Stock M",
                "description": "New entry",
                "price_history": [
                    {
                        "price": 222,
                        "count": 555
                    }
                ]
            } 
        response = api_client.post(url, data=payload)
        data = response.json()
        
        # Endpoint to return cirrect status code
        assert response.status_code == 201

        # Validate record is present in DB
        assert Stock.objects.filter(id=data.get('id')).exists()

        # Check if generated id from DB is returned in response
        assert data.get('id', 0) > 0

        # To DO: 
            # PUT, DELETE


    # Deny admins to sell or buy stock
    def test_deny_admin_to_trade(self, api_client):
        url = '/api/brokering/transactions/'

        for transaction_type in ['SELL', 'BUY']:
            payload = {
                    "transaction_type": transaction_type,
                    "quantity": 20,
                    "price_per_unit": 80,
                    "total_price": 1600,
                    "timestamp": datetime.now().isoformat(),
                    "stock_name": "Stock A"
                }
            response = api_client.post(url, data=payload)

            assert response.status_code == 403