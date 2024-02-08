from rest_framework import serializers
from django.db.models import F
from .models import Stock, StockPrice, Transaction, Holding


class StockPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockPrice
        fields = ['price', 'count', 'created_at', 'updated_at']


class StockSerializer(serializers.ModelSerializer):
    price_history = StockPriceSerializer(many=True, required=False)
    latest_price = serializers.SerializerMethodField()

    class Meta:
        model = Stock
        fields = ['id', 'name', 'description', 'created_at', 'updated_at', 'price_history', 'latest_price']

    def get_latest_price(self, obj):
        latest_price_obj = obj.price_history.last() #.latest('updated_at')
        if latest_price_obj:
            return {'price': latest_price_obj.price, 
                    'count':latest_price_obj.count,
                    'updated_at':latest_price_obj.updated_at}
        return None

    def create(self, validated_data):
        stock_prices_data = validated_data.pop('price_history', None)
        stock = Stock.objects.create(**validated_data)
        if stock_prices_data:
            StockPrice.objects.create(stock=stock, **stock_prices_data[0])  # Assuming there's only one stock price
        return stock


class TransactionSerializer(serializers.ModelSerializer):
    stock_name = serializers.CharField(allow_null=False, required=False)

    class Meta:
        model = Transaction
        fields = ['transaction_type', 'quantity', 'price_per_unit', 'total_price', 'timestamp', 'stock_name']

    def fetch_stock_obj(self, stock_name):
        try:
            stock = Stock.objects.get(name=stock_name)
            return stock
        except Stock.DoesNotExist:
            raise serializers.ValidationError({"detail" : f"Stock '{stock_name}' does not exist."})

    def create_stock_price_entry(self, validated_data):
        stock_obj = validated_data['stock']

        current_record = stock_obj.price_history.latest('created_at')
        if validated_data['transaction_type'] == 'BUY':
            updated_count = current_record.count - validated_data['quantity']
        elif validated_data['transaction_type'] == 'SELL': # Assumed that broker is buying all the stocks from investor
            updated_count = current_record.count + validated_data['quantity'] 
            
        # Future improvement :: To add additional logic to change new price
        updated_price = current_record.price

        StockPrice.objects.create(stock=stock_obj, price=updated_price, count=updated_count)


    def create_or_update_holdings(self, validated_data):
        quantity = validated_data['quantity']

        try:
            obj, created = Holding.objects.get_or_create(user=validated_data['user'], stock=validated_data['stock'])

            if created:
                # obj.quantity = F('quantity') - 1
                obj.quantity = quantity
            elif validated_data['transaction_type'] == 'BUY':
                obj.quantity += quantity
            elif validated_data['transaction_type'] == 'SELL':
                obj.quantity -= quantity

            obj.save()
        except Exception as e:
            return False     
        return True

    def create(self, validated_data): 

        transaction = Transaction.objects.create(**validated_data)

        if transaction:
            status = self.create_or_update_holdings(validated_data)
            if status:
                self.create_stock_price_entry(validated_data)
            else:
                # Notify Dev team
                print('DB entry not created on purchase')

        return transaction


    def validate(self, data):

        stock_name = data['stock_name']
        quantity = data['quantity']

        try:
            stock = Stock.objects.get(name=stock_name)
        except Stock.DoesNotExist:
            raise serializers.ValidationError({'detail': f'Broker does not deal {stock_name}'})

        # Fetch existing count from StockPrice model
        if data['transaction_type'] == 'BUY':
            current_stock_count = stock.price_history.latest('created_at').count
            if not quantity <= current_stock_count:
                message = f'Not enough stocks from {stock_name} existing count is {current_stock_count}'
                raise serializers.ValidationError({'detail': message})
        else:
            try:
                user = self.context['request'].user
                holding = Holding.objects.get(stock=stock, user=user)
                current_holding_count = holding.quantity
            except Holding.DoesNotExist:
                raise serializers.ValidationError({'detail': f'User does not have {stock_name} to trade'})

            if not current_holding_count > quantity:
                message = f'Not enough holding stocks from {stock_name} existing count is {current_holding_count}'
                raise serializers.ValidationError({'detail': message})

        # Attaching stock object for Transsaction create
        data.pop('stock_name')
        data['stock'] = stock

        return data


class HoldingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Holding
        fields = ['stock', 'quantity']
        depth = 1
