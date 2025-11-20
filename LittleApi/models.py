from django.db import models
from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin,BaseUserManager
from django.contrib.auth.models import Group
# Create your models here.




class BaseUtils(BaseUserManager):
    def create_user(self,username,email,password,group = None):
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(username=username,email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)

        if group:
            for item in group:
                user.groups.add(item)
            return user
        return user


    def create_superuser(self,username,email,password):
        user = self.create_user(username,email,password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser,PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100,unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    objects = BaseUtils()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username

    def save(self,*args,**kwargs):
        if not self.password.startswith('pbkdf2'):
            self.set_password(self.password)
        super().save(*args,**kwargs)


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length =255)
    price = models.FloatField()
    inventory = models.PositiveIntegerField(default=0 )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT , blank=True, null=True)


    def __str__(self):
        return self.name




class CartItem(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE , blank=True, null=True)
    menu_item = models.ForeignKey(MenuItem,on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.quantity > self.menu_item.inventory:
            raise ValueError('Not enough inventory')
        self.menu_item.inventory -= self.quantity
        self.menu_item.save()
        super().save(*args, **kwargs)
    

    def __str__(self):
        return 'cart of : ' +str(self.user.username) + ' \n menu item : ' + str(self.menu_item.name)
    


class Order(models.Model):
    STATUS_CHOICES = [
        (0, "Prête à livrer"),
        (1, "Livrée"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    delivery_team = models.ForeignKey(
        User,  
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_orders",
    )
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} - {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    menu_item = models.ForeignKey("MenuItem", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.menu_item.name} x{self.quantity}"


    

    

