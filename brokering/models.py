from django.db import models
from django.contrib.auth.models import User

class Stock(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'stock' 


class StockPrice(models.Model):
    stock = models.ForeignKey(Stock, related_name='price_history', on_delete=models.CASCADE)
    price = models.FloatField()
    count = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.stock.name}: {self.price}"
        
    class Meta:
        db_table = 'stock_price'


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    TRANSACTION_TYPES = [
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),]
    transaction_type = models.CharField(max_length=4, choices=TRANSACTION_TYPES)
    quantity = models.IntegerField()
    price_per_unit = models.FloatField()
    total_price = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} {self.transaction_type} {self.stock.name}"

    class Meta:
        db_table = 'transaction'


class Holding(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.stock.name}: {self.quantity}"

    class Meta:
        db_table = 'holding'