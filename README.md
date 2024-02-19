
# Stratipy Coding challange

#### Assumptions

* There is no commissions kept by the broker.
* When investor sells shares all will be bought by the Broker (Backend) and its existing counts will increase.
* Maintained sqlite DB without creating a db service in container for ease of use.
* Tables StockPrice and Transaction are created to specifically to hold historical data which would enable to run future analytics or debug transactions.
* Differentiation of Investor or Admin will be decided through django built in is_staff flag. Once user register thorough register endpoint, Super admin can provide them Admin rights from django admin dashboar.

#### Database

I have created following models to hold data for the backend. 
* **Stock** : Meta table to hold name and desctions of the stocks
* **StockPrice** : Holds 1-N realtionship with **Stock**. StockPrice will hold historical data of each price change from Admins, Buy/SELL from Investors random generations from the scheduled job. Only the **latest** record will be fetched for backend logics.  
* **Transaction** : Will hold historical data of each Buy and Sell of each user 
* **Holding** : Holds all data of each users holdings.


#### API Testing

I am currently using Insomnia which can be downloaded from https://insomnia.rest/download. Please import the **insomina_dump.json** to your insomnia application. In each request navigate to *Bearer -> Token -> Request*. from the drop down you can select the user type to be login_investor or login_staff to navigate different user roles fo each endpoint.


Created docker compose to simplify to spawn a container. To build container run
```http
  docker-compose build
```
Django will run on port 8000 using gunicorn production server to run the application 
run
```http
  docker-compose up
```

Within the the container ther will be a seperate service to run a management command which is at location. Script is scheduled to run every 30 seconds (plus 1) as a seperate service within the container.
**brokering/management/commands/random_stock.py**



## API Reference for Django CRUD


#### Register user 

```http
  POST http://127.0.0.1:8000/api/users/register/
```
Sample body, returns 400 if user already exists
```json
{
	"username": "test",
	"password": "test"
}
```

#### Login and fetch token (auto configured in Insomnia) 
By default user will be an investor please set is_staff falg to make user an Admin
```http
POST http://127.0.0.1:8000/api/users/login/
```
Sample body,
```json
{
	"username": "test",
	"password": "test"
}
```

## API Reference for Stock management and view
#### Listing stocks
```http
  GET 127.0.0.1:8000/api/brokering/stocks
```

#### Updating a stock by PK 
```http
  PUT 127.0.0.1:8000/api/brokering/stocks/1/
```
```json
{
		"name": "Stock A",
    "description": "Updated stock description"
}
```

#### Creating a stock
```http
  POST 127.0.0.1:8000/api/brokering/stocks/
```

Sample data
```json
{
	"name": "Stock Z",
	"description": "New entry",
	"price_history": [
		{
			"price": 222,
			"count": 555
		}
	]
}
```

#### Deleting a stock
```http
  DELETE 127.0.0.1:8000/api/brokering/stocks/<PK>
```


## API Reference for transaction (Buy/Sell)
Buy or Sell will be differentiated by the *transaction_type* key
```http
  POST 127.0.0.1:8000/api/brokering/transactions/
```
For Buying stocks : 

	{
		"transaction_type": "BUY",
		"quantity": 200,
		"price_per_unit": 40,
		"total_price": 8000,
		"timestamp": "{% now 'iso-8601', '' %}",
		"stock_name": "Stock A"
	}
For selling stocks :

	{
		"transaction_type": "SELL",
		"quantity": 20,
		"price_per_unit": 80,
		"total_price": 1600,
		"timestamp": "{% now 'iso-8601', '' %}",
		"stock_name": "Stock A"
	}


## API Reference for viewing of Holdings of current user
```http
  GET 127.0.0.1:8000/api/brokering/holdings/
```
	{
		"transaction_type": "SELL",
		"quantity": 20,
		"price_per_unit": 80,
		"total_price": 1600,
		"timestamp": "{% now 'iso-8601', '' %}",
		"stock_name": "Stock A"
	}

## Testing

For testing, I have used Pytest and Pytest-factoryboy to create dummy data for testing (included in requirments.txt). Testing can be found under [tests/](https://github.com/isara-ovin/stock-broker/tree/main/tests). I have created test cases to validate user roles as per the coding task. And created test cases for transaction api (buy).

Run command **pytest** in the root directory to run the test cases 

#### Test Cases under test_user_roles.py
* Only admins are allowed to create stock
* Admins can not Buy or Sell stock
* Investors are not allowed to edit stocks (POST, PUT, DELETE)


#### Test Cases under test_transactions.py
* Investor can buy existing stocks
* Records create or updates in Holdings table
* Record increments its value when buying valid stock
* Investor can't buy non-existing stocks
