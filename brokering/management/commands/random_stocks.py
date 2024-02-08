from django.core.management.base import BaseCommand 
from brokering.models import Stock, StockPrice 

import schedule
import time

from random import randint


def job():
    stock_names = Stock.objects.all()

    for stock in stock_names:
        price = randint(10, 100)
        count = randint(2000, 6000)
        StockPrice.objects.update_or_create(stock=stock, price=price, count=count)

        print(f"Updating for {stock.name}")

class Command(BaseCommand): 
    help = 'Runs every  30 second to populate StockPrice table'
  
    def handle(self, *args, **kwargs): 

        schedule.every(30).seconds.do(job)

        while True:
            schedule.run_pending()
            time.sleep(1)