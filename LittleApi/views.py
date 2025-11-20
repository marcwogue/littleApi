from rest_framework import generics,filters,permissions, viewsets
from rest_framework.views import APIView, status
from .serializers import   CartItemSerializer, MenuItemsSerializer, OrderSerializer,UserSerializer,MyTokenObtainPairSerializer
from .models import  CartItem, MenuItem, Order,User
from rest_framework_simplejwt.views import TokenObtainPairView
from . import custompermissions

# Create your views here.


class LoginView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class UserView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        permission = [permissions.IsAuthenticated]
        if self.request.method == 'POST':
            permission = [permissions.AllowAny]
        elif self.request.method == 'GET':
            permission = [custompermissions.IsAdmin | custompermissions.IsManager]
        return [permited() for permited in permission]

class UserMeView(generics.ListAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    def get_permissions(self):
        permission = [permissions.IsAuthenticated]
        return [permited() for permited in permission]

class UserModView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        permission = [permissions.IsAuthenticated]
        if self.request.method == 'PUT' and self.kwargs['pk'] == self.request.user.id:
            permission = [permissions.AllowAny]
        elif self.request.method == 'DELETE' and self.kwargs['pk'] == self.request.user.id:
            permission = [custompermissions.IsLivrer | custompermissions.IsManager | custompermissions.IsClient]
        elif self.request.method == 'DELETE':
            permission = [custompermissions.IsLivrer | custompermissions.IsManager]
        return [permited() for permited in permission] 


class MenuItemView (generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemsSerializer

    

    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['create_at']
    ordering_fields = ['price']
    search_fields = ['name']

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_permissions(self):
        permission = [permissions.IsAuthenticated]
        if self.request.method == 'GET':
            permission = [permissions.AllowAny]
        elif self.request.method == 'POST':
            permission = [custompermissions.IsManager]
        return [permited() for permited in permission]

class MenuItemModView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemsSerializer
    

    def get_permissions(self):
        permission = [custompermissions.IsManager]
        return [permited() for permited in permission] 


class CartItemView(generics.ListCreateAPIView):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer  

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return CartItem.objects.filter(user=self.request.user)
        return super().get_queryset()




    


class ClearCartView(APIView):
    permission_classes = [permissions.IsAuthenticated, custompermissions.IsClient]

    def delete(self, request):
        user = request.user
        deleted_count, _ = CartItem.objects.filter(user=user).delete()

        return Response(
            {"message": f"{deleted_count} items supprimés"},
            status=status.HTTP_200_OK
        )



class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # Client → voir seulement ses commandes
        if user.groups.filter(name="Client").exists():
            return Order.objects.filter(user=user)

        # Delivery → voir seulement commandes assignées à son équipe
        if user.groups.filter(name="Delivery").exists():
            return Order.objects.filter(delivery_team=user)

        # Manager/Admin → tout voir
        return Order.objects.all()

    def perform_update(self, serializer):
        user = self.request.user

        # Delivery team ne peut changer que le statut
        if user.groups.filter(name="Delivery").exists():
            serializer.save(status=serializer.validated_data.get("status"))
        else:
            serializer.save()