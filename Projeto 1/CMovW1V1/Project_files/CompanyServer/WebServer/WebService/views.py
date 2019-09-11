from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from django.http import JsonResponse
from rest_framework.status import (
	HTTP_400_BAD_REQUEST,
	HTTP_404_NOT_FOUND,
	HTTP_200_OK,
	HTTP_201_CREATED,
	HTTP_406_NOT_ACCEPTABLE
)
from rest_framework.response import Response

from rest_framework import viewsets, mixins
import random
from WebService.models import User, Performance, Ticket, CafeteriaVoucher, CafeteriaOrder
from WebService.serializers import UserSerializer, PerformanceSerializer, TicketSerializer, CafeteriaVoucherSerializer, CafeteriaOrderSerializer
from WebService.utils import getCafeteriaOrderPrice, isTicketValid, generateVoucher, isSignatureValid
from django.db.models import Q
import json
from datetime import datetime
import uuid


#formato do header para autenticar exemplo:
#Authorization Token 4c2fd1a716d87c814ffbcebfbbad9b77f5106324

COFFEE_PRICE = 1
POPCORN_PRICE = 0.5
SODA_PRICE = 1
SANDWICH_PRICE = 2



class usersViewSet(viewsets.ModelViewSet):
	serializer_class = UserSerializer
	permission_classes = [] #override default permissions, so no permissions needed, anyone can "POST" and "GET"
	
	def get_queryset(self): #GET request
		return User.objects.all()

	def create(self, request, *args, **kwargs): #override create so it responds only with id and the token
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		self.perform_create(serializer)
		headers = self.get_success_headers(serializer.data)
		newUser = serializer.instance
		token, _  = Token.objects.get_or_create(user=newUser)
		return Response({'id':newUser.id, 'token': token.key}, status = HTTP_201_CREATED, headers=headers)

	def perform_create(self, serializer):  #POST request
		instance = serializer.save()
		instance.set_password(instance.password) #hash password
		instance.save()




#Login, returns user token
"""
{
"username":user,
"password":qwerty123
}
"""
@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def login(request):
	username = request.data.get("username")
	password = request.data.get("password")
	if username is None or password is None:
		return Response({'error': 'Please provide both username and password'}, status=HTTP_400_BAD_REQUEST)
	user = authenticate(username=username, password=password)
	if not user:
		return Response({'error': 'Invalid Credentials'}, status=HTTP_404_NOT_FOUND)
	token, _ = Token.objects.get_or_create(user=user)
	response_data = {}
	response_data['token'] = token.key
	response_data['userID'] = user.id

	return Response(response_data, status=HTTP_200_OK)




#Can only GET the performances, if is authenticated
class performanceViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
	serializer_class = PerformanceSerializer
	permission_classes = [IsAuthenticated]

	def get_queryset(self): #GET request
		return Performance.objects.all()




#user, when authenticated, can GET their tickets
class ticketViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
	serializer_class = TicketSerializer
	permission_classes = [IsAuthenticated]

	def get_queryset(self): #GET request
		return Ticket.objects.all().filter(user=self.request.user)






"""
Buy tickets
{
"performanceID": 2,
"numberOfTickets": 6,
"signature": "fhqw3thq893htq389ghq389ghq389htg"
""

}
The user needs to be authenticated and can buy tickets for the specified performance

It is generated a voucher for each ticket and a 5% discount voucher each time
	the money spent passes the 100 euros multiple

returns the bought tickets info
"""
@csrf_exempt
@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def buyPerformanceTickets(request):
	performanceID = request.data.get("performanceID")
	numberOfTickets = request.data.get("numberOfTickets")
	signature = request.data.get("signature")
	if performanceID is None or numberOfTickets is None or signature is None:
		return Response({'error': 'Please provide both performane id, number of tickets signed correctly'}, status=HTTP_400_BAD_REQUEST)

	if not isSignatureValid(signature, request.user):
		return Response({'error': 'Invalid Signature'}, status=HTTP_406_NOT_ACCEPTABLE)

	try:
		performance = Performance.objects.get(id=performanceID)
	except:
		return Response({'error': 'Performance does not exist'}, status=HTTP_400_BAD_REQUEST)
	tickets = []
	vouchers = []
	moneySpent = 0
	timeNow = datetime.now()
	for x in range(numberOfTickets):
		moneySpent +=  performance.price
		tickets.append(Ticket(used=False, place=random.randint(1,3000), performance=performance, user=request.user, created_at=timeNow))
		if moneySpent >= 100:
			while moneySpent >= 100:
				moneySpent-=100
				vouchers.append(generateVoucher(True, request.user))
		vouchers.append(generateVoucher(False, request.user))

	Ticket.objects.bulk_create(tickets)
	CafeteriaVoucher.objects.bulk_create(vouchers)

	newTicketsList = Ticket.objects.filter(created_at=timeNow)

	response_data = {}
	response_data['performanceID'] = performance.id
	serializer = TicketSerializer(newTicketsList, many=True)
	response_data['tickets'] = serializer.data

	return Response(response_data, status=HTTP_200_OK)







"""
Validates the tickets, the user needs to be authenticated

{
"userID": "b91bfe4f-2c00-431e-8768-d1c1f55e6b31",
"ticket1ID": 4,
"ticket2ID": 2,
"ticket3ID": 6,
"ticket4ID": 3
}
If you dont want to specify the ticket, pass the value -1

A ticket is valid if it is from the user, exits and hasnt been used
"""
@csrf_exempt
@api_view(["POST"])
@permission_classes(())
def validateTickets(request):
	userID = ""
	ticket1ID = ticket2ID = ticket3ID = ticket4ID = -1

	try:
		userID = request.data['userID']
		ticket1ID = request.data['ticket1ID']
		ticket2ID = request.data['ticket2ID']
		ticket3ID = request.data['ticket3ID']
		ticket4ID = request.data['ticket4ID']

	except:
		return Response({'errorMsg':"Error validating vouchers"}, status = HTTP_400_BAD_REQUEST)

	try:
		user = User.objects.get(id=userID)
	except:
		return Response({'error': 'User does not exist'}, status=HTTP_400_BAD_REQUEST)


	response_data = {}

	if ticket1ID > 0:
		if(isTicketValid(ticket1ID, user)):
			Ticket.objects.filter(Q(user=user) & Q(id=ticket1ID)).update(used=True)
			response_data['ticket1Valid'] = 'true'
		else: response_data['ticket1Valid'] = 'false'
	if ticket2ID > 0:
		if(isTicketValid(ticket2ID, user)):
			Ticket.objects.filter(Q(user=user) & Q(id=ticket2ID)).update(used=True)
			response_data['ticket2Valid'] = 'true'
		else: response_data['ticket2Valid'] = 'false'
	if ticket3ID > 0:
		if(isTicketValid(ticket3ID, user)):
			Ticket.objects.filter(Q(user=user) & Q(id=ticket3ID)).update(used=True)
			response_data['ticket3Valid'] = 'true'
		else: response_data['ticket3Valid'] = 'false'
	if ticket4ID > 0:
		if(isTicketValid(ticket4ID, user)):
			Ticket.objects.filter(Q(user=user) & Q(id=ticket4ID)).update(used=True)
			response_data['ticket4Valid'] = 'true'
		else: response_data['ticket4Valid'] = 'false'

	return  Response(response_data, status = HTTP_200_OK)


"unused tickets"
class unusedTicketViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
	serializer_class = TicketSerializer
	permission_classes = [IsAuthenticated]

	def get_queryset(self): #GET request
		return Ticket.objects.all().filter(Q(user=self.request.user) & Q(used=False))












"""
Allows to see the user vouchers, needs to be authenticated
"""
class cafeteriaVoucherViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
	serializer_class = CafeteriaVoucherSerializer
	permission_classes = [IsAuthenticated]

	def get_queryset(self): #GET request
		return CafeteriaVoucher.objects.all().filter(user=self.request.user)


"""
Allows to see the user UNUSED vouchers, needs to be authenticated
"""
class unusedCafeteriaVoucherViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
	serializer_class = CafeteriaVoucherSerializer
	permission_classes = [IsAuthenticated]

	def get_queryset(self): #GET request
		return CafeteriaVoucher.objects.all().filter(Q(user=self.request.user) & Q(used=False))






"""
Lets GET all the user cafeteria order and create orders, with POST
[
"voucher1ID": -1,
"voucher2ID": 4,
"coffees_quantity":1,
"popcorn_quantity":3,
"soda_quantity":1,
"sandwich_quantity":0,
"signature": "fhqw3thq893htq389ghq389ghq389htg"
}

If you dont want to use a voucher, set the id to -1

POST:
First verifies if the vouchers are valid (if they are from the user and exist
	and if they arent two 5$ discount vouchers

If the vouchers are good, creates a new order and returns the full order information
"""
class cafeteriaOrderViewSet(viewsets.ModelViewSet):
	serializer_class = CafeteriaOrderSerializer
	permission_classes = [IsAuthenticated]

	def get_queryset(self): #GET request
		return CafeteriaOrder.objects.all().filter(user=self.request.user)

	def create(self, request, *args, **kwargs): #override create so it responds custom response
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		vouchersError = self.perform_create(serializer)
		if vouchersError == -1:
			return Response({'errorMsg':"Can't use those vouchers"}, status = HTTP_400_BAD_REQUEST)
		elif vouchersError == -2:
			return Response({'errorMsg':"Can't two 5% discount vouchers at the same time"}, status = HTTP_400_BAD_REQUEST)
		elif vouchersError == -3:
			return Response({'errorMsg': 'Invalid Signature'}, status=HTTP_406_NOT_ACCEPTABLE)
		headers = self.get_success_headers(serializer.data)
		newOrder = serializer.instance
		priceToPay = getCafeteriaOrderPrice(newOrder.voucher1ID,
											newOrder.voucher2ID,
											newOrder.coffees_quantity,
											newOrder.popcorn_quantity,
											newOrder.soda_quantity,
											newOrder.sandwich_quantity)

		CafeteriaOrder.objects.filter(id=newOrder.id).update(price=priceToPay)

		response_data = {}
		response_data['orderNumber'] = newOrder.id
		response_data['coffeesQty'] = newOrder.coffees_quantity
		response_data['popcornQty'] = newOrder.popcorn_quantity
		response_data['sodaQty'] = newOrder.soda_quantity
		response_data['sandwichQty'] = newOrder.sandwich_quantity

		if newOrder.voucher1ID > 0:
			response_data['voucher1Valid'] = 'true'
		if newOrder.voucher2ID > 0:
			response_data['voucher2Valid'] = 'true'

		response_data['priceToPay'] = priceToPay
		response_data['nif'] = request.user.nif

		return Response(response_data, status = HTTP_200_OK, headers=headers)


	#return 0, ok, else vouchers error
	def perform_create(self, serializer):  #POST request
		#signature verification
		signature = self.request.data.get("signature")
		if signature is None:
			return -3
		if not isSignatureValid(signature, self.request.user):
			return -3

		#vouchers verification
		if serializer.validated_data['voucher1ID'] > 0 or serializer.validated_data['voucher2ID'] > 0:
			vouchers = CafeteriaVoucher.objects.all().filter(
									(Q(user=self.request.user) & Q(id=serializer.validated_data['voucher1ID'])) |
									(Q(user=self.request.user) & Q(id=serializer.validated_data['voucher2ID'])))

			if not vouchers.exists():
				return -1 #cant use any of the given vouchers, they are not mine
			if serializer.validated_data['voucher1ID'] == serializer.validated_data['voucher2ID']:
				return -1 #cant use the same voucher twice
			else:
				if vouchers.count() > 1:
					if vouchers[0].type == CafeteriaVoucher.DISCOUNT_5 & vouchers[1].type == CafeteriaVoucher.DISCOUNT_5:
						return  -2 #cant use two 5% discound vouchers at the same time
					else:
						instance = serializer.save(user=self.request.user)
						return 0
				else:
					instance = serializer.save(user=self.request.user)
					return 0
		else:
			instance = serializer.save(user=self.request.user)
			return 0




"unpaid tickets"
class unpaidCafeteriaOrderViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
	serializer_class = CafeteriaOrderSerializer
	permission_classes = [IsAuthenticated]

	def get_queryset(self): #GET request
		return CafeteriaOrder.objects.all().filter(Q(user=self.request.user) & Q(paid=False))





"""
Pays the order, user needs to be authenticated
{
"orderID": 41,
"userID": "b91bfe4f-2c00-431e-8768-d1c1f55e6b31",
"signature": "fhqw3thq893htq389ghq389ghq389htg"
}

if the price to pay is > 100 euros, generates a new 5% discount

returns which vouchers were valid and the price paid
"""
@csrf_exempt
@api_view(["POST"])
@permission_classes(())
def payCafeteriaOrder(request):
	try:
		orderID = request.data['orderID']
		userID = request.data['userID']
		signature = request.data["signature"]
	except:
		return Response({'errorMsg':"Error reading order"}, status = HTTP_400_BAD_REQUEST)

	try:
		user = User.objects.get(id=userID)
	except:
		return Response({'errorMsg': 'User does not exist'}, status=HTTP_400_BAD_REQUEST)


	if not isSignatureValid(signature, user):
		return Response({'errorMsg': 'Invalid Signature'}, status=HTTP_406_NOT_ACCEPTABLE)


	try:
		cafeteriaOrder = CafeteriaOrder.objects.get(Q(id=orderID) & Q(user=user))
	except:
		return Response({'errorMsg': 'Cant find that order'}, status=HTTP_400_BAD_REQUEST)


	if cafeteriaOrder.paid == True:
		return Response({'errorMsg': 'Order already paid'}, status=HTTP_406_NOT_ACCEPTABLE)



	priceToPay = getCafeteriaOrderPrice(cafeteriaOrder.voucher1ID, cafeteriaOrder.voucher2ID,
										cafeteriaOrder.coffees_quantity, cafeteriaOrder.popcorn_quantity,
										cafeteriaOrder.soda_quantity, cafeteriaOrder.sandwich_quantity)

	if priceToPay >= 100:
		generateVoucher(True, user)

	response_data = {}

	if cafeteriaOrder.voucher1ID > 0:
		CafeteriaVoucher.objects.filter(id=cafeteriaOrder.voucher1ID).update(used=True)
		response_data['voucher1Valid'] = 'true'
	else: response_data['voucher1Valid'] = 'false'
	if cafeteriaOrder.voucher2ID > 0:
		CafeteriaVoucher.objects.filter(id=cafeteriaOrder.voucher2ID).update(used=True)
		response_data['voucher2Valid'] = 'true'
	else: response_data['voucher2Valid'] = 'false'

	CafeteriaOrder.objects.filter(Q(id=orderID) & Q(user=user)).update(paid=True)
	response_data['pricePaid'] = priceToPay

	return Response(response_data, status = HTTP_200_OK)


