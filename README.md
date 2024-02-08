
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

Configured two routers from the root ```api/``` for the each section of the task
browsable api is available at http://127.0.0.1:8000/api/

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