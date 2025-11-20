
from rest_framework import serializers
from .models import  CartItem, MenuItem, Order, OrderItem,User
from django.contrib.auth.models import Group
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

class MenuItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = '__all__'


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email
        token['is_staff'] = user.is_staff
        token['groups'] = list(user.groups.values_list('name', flat=True))
        print(token.get('username'))
        # tu peux ajouter d'autres champs

        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['username'] = self.user.username
        data['email'] = self.user.email
        data['is_staff'] = self.user.is_staff
        data['groups'] = list(self.user.groups.values_list('name', flat=True))
        return data




class UserSerializer(serializers.ModelSerializer):
   
    groups = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(),
        many=True,
        read_only=False,
        write_only=False,
    )
    class Meta:
        model = User
        fields =   ('groups','username','email','password')

class CartItemSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)
    menu_name = serializers.CharField(source='menu_item.name', read_only=True)
    menu_item = serializers.PrimaryKeyRelatedField(
        queryset=MenuItem.objects.all(),
        write_only=True,
    )
    class Meta:
        model = CartItem
        fields = ['user','menu_item','id','quantity','added_at','updated_at','menu_name']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return CartItem.objects.create(**validated_data)



class OrderItemSerializer(serializers.ModelSerializer):
    menu_name = serializers.CharField(source="menu_item.name", read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "menu_item", "menu_name", "quantity"]


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.username", read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "user", "delivery_team", "status", "created_at", "updated_at", "items"]

    def create(self, validated_data):
        user = self.context["request"].user
        order = Order.objects.create(user=user, **validated_data)

        # Copier les items du panier dans la commande
        cart_items = CartItem.objects.filter(user=user)
        order_items = [
            OrderItem(order=order, menu_item=item.menu_item, quantity=item.quantity)
            for item in cart_items
        ]
        OrderItem.objects.bulk_create(order_items)

        # Vider le panier
        cart_items.delete()

        return order