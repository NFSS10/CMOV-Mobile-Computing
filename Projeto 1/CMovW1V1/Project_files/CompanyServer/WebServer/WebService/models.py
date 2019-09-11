from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import datetime
import uuid
from django.core.validators import MaxValueValidator

class User(AbstractUser): #extended from the Already base implementation of django user
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, null=False)
	nif = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(999999999)], blank=True)
	creditcard_number = models.CharField(default="0000000000000000",max_length=16, blank=True)
	#Credit Card Type
	MASTERCARD = 1
	VISA = 2
	AMERICANEXPRESS = 3
	TYPES_CHOICE = (
		(MASTERCARD, 'Mastercard'),
		(VISA, 'VISA'),
		(AMERICANEXPRESS, 'American Express'),
	)
	cc_type = models.IntegerField(choices=TYPES_CHOICE, default=VISA)
	cc_validity = models.CharField(default="00/00", max_length=5, blank=True)
	public_key = models.CharField(default="", max_length=256, blank=True)
	
	def __str__(self):
		return self.username + " with id " + str(self.id)


class Performance(models.Model):
	name = models.CharField(max_length=128, blank=False, null=False)
	startDate = models.DateTimeField(blank=False, null=False)
	price = models.PositiveIntegerField(blank=True)	
	
	def __str__(self):
		return str(self.name)


class Ticket(models.Model):
	used = models.BooleanField(default=False)
	place = models.PositiveIntegerField(blank=True)
	performance = models.ForeignKey(Performance, on_delete=models.CASCADE, blank=True, null=False)
	user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=False)
	created_at = models.DateTimeField(default=datetime.now, blank=True, null=True)
	
	def __str__(self):
		return "Ticket " + str(self.id) + " for " + str(self.performance)



class CafeteriaVoucher(models.Model):
	used = models.BooleanField(default=False)
	user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=False)
	#Type
	FREE_COFFEE = 1
	FREE_POPCORN = 2
	FREE_SODA = 3
	FREE_SANDWICH = 4
	DISCOUNT_5 = 5
	TYPES_CHOICE = (
		(FREE_COFFEE, 'Free Coffee'),
		(FREE_POPCORN, 'Free Popcorn'),
		(FREE_SODA, 'Free Soda'),
		(FREE_SANDWICH, 'Free Sandwich'),
		(DISCOUNT_5, '5% Discount'),
	)
	type = models.IntegerField(choices=TYPES_CHOICE, default=FREE_COFFEE)
	
	def __str__(self):
		return "Voucher " + str(self.id) + " of user " + str(self.user.username)


class CafeteriaOrder(models.Model):
    paid = models.BooleanField(default=False)
    voucher1ID = models.IntegerField(default=-1)
    voucher2ID = models.IntegerField(default=-1)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=False)
    coffees_quantity = models.PositiveIntegerField(default=0)
    popcorn_quantity = models.PositiveIntegerField(default=0)
    soda_quantity = models.PositiveIntegerField(default=0)
    sandwich_quantity = models.PositiveIntegerField(default=0)
    price = models.PositiveIntegerField(default=0, blank=True)

    def __str__(self):
        return "Order " + str(self.id) + " of user " + str(self.user.username)
