from django.test import TestCase, RequestFactory
from rest_framework.test import APIRequestFactory, APIClient
from rest_framework.test import RequestsClient


from .models import Performance, Ticket, CafeteriaVoucher, CafeteriaOrder, User
import WebService.views


class EventTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        user1 = User(username="user1", nif=123456789, creditcard_number="0000000000000000", cc_type=1, cc_validity="12/20", public_key="blablablabla123ABC")
        user1.set_password("12345")
        user1.save()

        performance1 = Performance(name="Performance 1", startDate="2006-10-25 14:30:59", price=399)
        performance1.save()

        performance2 = Performance(name="Performance 2", startDate="2006-10-25 14:30:59", price=50)
        performance2.save()


    def test_registerUser(self):
        jsonData = {}
        jsonData['username'] = "User2"
        jsonData['password'] = "12345"
        jsonData['nif'] = 12345678
        jsonData['creditcard_number'] = "0000000000000000"
        jsonData['cc_type'] = 1
        jsonData['cc_validity'] = "10/20"
        jsonData['public_key'] = "123blablabalAFQW3T9"

        client = APIClient()
        response = client.post('/api/users/', jsonData, format='json')

        newUser = User.objects.get(username="User2")
        assert newUser.username == "User2"






    def test_getPerformances(self):
        user1 = User.objects.get(username="user1")
        client = APIClient()
        client.force_authenticate(user=user1)

        response = client.get('/api/performances/')
        assert response.data['results'][0]['name'] == "Performance 1"
        assert response.data['results'][1]['name'] == "Performance 2"






    def test_tickets_and_vouchers(self):
        user1 = User.objects.get(username="user1")
        client = APIClient()
        client.force_authenticate(user=user1)

        #user1 has 0 tickets and...
        response = client.get('/api/tickets/')
        assert response.data['count'] == 0
        # 0 vouchers
        response = client.get('/api/cafeteriaVouchers/')
        assert response.data['count'] == 0


        #performance doesnt exist
        jsonData = {}
        jsonData['performanceID'] = 4
        jsonData['numberOfTickets'] = 1
        jsonData['signature'] = "assinaturaTesteDebugPurpose"
        response = client.post('/api/buyTickets', jsonData, format='json')
        assert response.status_code == 400
        assert response.data['error'] == "Performance does not exist"


        #buying one ticket for performance 1
        #sucess and ...
        jsonData = {}
        jsonData['performanceID'] = 1
        jsonData['numberOfTickets'] = 1
        jsonData['signature'] = "assinaturaTesteDebugPurpose"
        response = client.post('/api/buyTickets', jsonData, format='json')
        assert response.status_code == 200
        #the user should have 1 ticket and ...
        response = client.get('/api/tickets/')
        assert response.data['count'] == 1
        #4 vouchers
        response = client.get('/api/cafeteriaVouchers/')
        assert response.data['count'] == 4
        #1 is free stuff and the other 3 are 5% discount
        numberOfdiscounts = 0
        if response.data['results'][0]['type'] == CafeteriaVoucher.DISCOUNT_5:
                numberOfdiscounts+=1
        if response.data['results'][1]['type'] == CafeteriaVoucher.DISCOUNT_5:
            numberOfdiscounts+=1
        if response.data['results'][2]['type'] == CafeteriaVoucher.DISCOUNT_5:
            numberOfdiscounts+=1
        if response.data['results'][3]['type'] == CafeteriaVoucher.DISCOUNT_5:
            numberOfdiscounts+=1
        assert numberOfdiscounts == 3


        #buying two ticket for performance 2
        jsonData = {}
        jsonData['performanceID'] = 2
        jsonData['numberOfTickets'] = 2
        jsonData['signature'] = "assinaturaTesteDebugPurpose"
        response = client.post('/api/buyTickets', jsonData, format='json')
        assert response.status_code == 200
        #the user should have 3 ticket and ...
        response = client.get('/api/tickets/')
        assert response.data['count'] == 3
        #7 vouchers
        response = client.get('/api/cafeteriaVouchers/')
        assert response.data['count'] == 7
        #3 is free stuff and the other 4 are 5% discount
        numberOfdiscounts = 0
        if response.data['results'][0]['type'] == CafeteriaVoucher.DISCOUNT_5:
            numberOfdiscounts+=1
        if response.data['results'][1]['type'] == CafeteriaVoucher.DISCOUNT_5:
            numberOfdiscounts+=1
        if response.data['results'][2]['type'] == CafeteriaVoucher.DISCOUNT_5:
            numberOfdiscounts+=1
        if response.data['results'][3]['type'] == CafeteriaVoucher.DISCOUNT_5:
            numberOfdiscounts+=1
        if response.data['results'][4]['type'] == CafeteriaVoucher.DISCOUNT_5:
            numberOfdiscounts+=1
        if response.data['results'][5]['type'] == CafeteriaVoucher.DISCOUNT_5:
            numberOfdiscounts+=1
        if response.data['results'][6]['type'] == CafeteriaVoucher.DISCOUNT_5:
            numberOfdiscounts+=1
        assert numberOfdiscounts == 4



        #----------validateTickets---------------
        #Ticket 10 doesnt exist, so it should not validate, ticket2ID is set as -1, so is not set and should not be in the response, ticket3 and ticket 4 are valid
        jsonData = {}
        jsonData['userID'] = user1.id
        jsonData['ticket1ID'] = 10
        jsonData['ticket2ID'] = -1
        jsonData['ticket3ID'] = 1
        jsonData['ticket4ID'] = 2
        #Tickets 1 and 2 not validated yet, so not used yet
        response = client.get('/api/tickets/1/')
        assert response.data['used'] == False
        response = client.get('/api/tickets/2/')
        assert response.data['used'] == False
        response = client.post('/api/validateTickets', jsonData, format='json')
        assert response.data['ticket1Valid'] == "false"
        assert response.data['ticket3Valid'] == "true"
        assert response.data['ticket4Valid'] == "true"
        #Tickets 1 and 2 validated, so are now marked as used
        response = client.get('/api/tickets/1/')
        assert response.data['used'] == True
        response = client.get('/api/tickets/2/')
        assert response.data['used'] == True





    def test_cafeteria_order_voucher_doesnt_exist(self):
        user1 = User.objects.get(username="user1")
        client = APIClient()
        client.force_authenticate(user=user1)

        #user1 has 0 cafeteria orders
        response = client.get('/api/cafeteriaOrders/')
        assert response.data['count'] == 0
        # and 0 vouchers
        response = client.get('/api/cafeteriaVouchers/')
        assert response.data['count'] == 0

        jsonData = {}
        jsonData['voucher1ID'] = 1 #this doesnt exist
        jsonData['voucher2ID'] = -1 #doesnt count this one
        jsonData['coffees_quantity'] = 1
        jsonData['popcorn_quantity'] = 1
        jsonData['soda_quantity'] = 1
        jsonData['sandwich_quantity'] = 1
        jsonData['signature'] = "assinaturaTesteDebugPurpose"
        response = client.post('/api/cafeteriaOrders/', jsonData, format='json')
        #error with vouchers
        assert response.status_code == 400
        assert response.data['errorMsg'] == "Can't use those vouchers"
        response = client.get('/api/cafeteriaOrders/')
        assert response.data['count'] == 0 #doesnt create
        assert response.status_code == 200



    def test_cafeteria_order_voucher_two_five_pecent_dicount(self):
        user1 = User.objects.get(username="user1")
        client = APIClient()
        client.force_authenticate(user=user1)

        #user1 has 0 cafeteria orders
        response = client.get('/api/cafeteriaOrders/')
        assert response.data['count'] == 0
        # and 0 vouchers
        response = client.get('/api/cafeteriaVouchers/')
        assert response.data['count'] == 0


        #buying one ticket for performance 1 to have 4 vouchers in wich 3 are discount 5
        jsonData = {}
        jsonData['performanceID'] = 1
        jsonData['numberOfTickets'] = 1
        jsonData['signature'] = "assinaturaTesteDebugPurpose"
        response = client.post('/api/buyTickets', jsonData, format='json')
        # now he has 4 vouchers and 3 are 5% discount
        response = client.get('/api/cafeteriaVouchers/')
        assert response.data['count'] == 4
        assert response.data['results'][0]['type'] == CafeteriaVoucher.DISCOUNT_5
        assert response.data['results'][1]['type'] == CafeteriaVoucher.DISCOUNT_5


        #trying to create order with two 5% discount
        jsonData = {}
        jsonData['voucher1ID'] = 1
        jsonData['voucher2ID'] = 2
        jsonData['coffees_quantity'] = 1
        jsonData['popcorn_quantity'] = 1
        jsonData['soda_quantity'] = 1
        jsonData['sandwich_quantity'] = 1
        jsonData['signature'] = "assinaturaTesteDebugPurpose"
        response = client.post('/api/cafeteriaOrders/', jsonData, format='json')

        #error with vouchers
        assert response.status_code == 400
        assert response.data['errorMsg'] == "Can't two 5% discount vouchers at the same time"
        #and it doesnt create as expected
        response = client.get('/api/cafeteriaOrders/')
        assert response.data['count'] == 0 #doesnt create
        assert response.status_code == 200





    def test_cafeteria_orders_without_vouchers(self):
        user1 = User.objects.get(username="user1")
        client = APIClient()
        client.force_authenticate(user=user1)

        #user1 has 0 cafeteria orders
        response = client.get('/api/cafeteriaOrders/')
        assert response.data['count'] == 0
        # and 0 vouchers
        response = client.get('/api/cafeteriaVouchers/')
        assert response.data['count'] == 0


        #make order without vouchers
        jsonData = {}
        jsonData['voucher1ID'] = -1
        jsonData['voucher2ID'] = -1
        jsonData['coffees_quantity'] = 1
        jsonData['popcorn_quantity'] = 1
        jsonData['soda_quantity'] = 1
        jsonData['sandwich_quantity'] = 1
        jsonData['signature'] = "assinaturaTesteDebugPurpose"
        response = client.post('/api/cafeteriaOrders/', jsonData, format='json')
        assert response.data['priceToPay'] == WebService.views.COFFEE_PRICE + WebService.views.SODA_PRICE + WebService.views.POPCORN_PRICE + WebService.views.SANDWICH_PRICE

        #should have one not paid order
        response = client.get('/api/cafeteriaOrders/')
        assert response.data['count'] == 1
        assert response.data['results'][0]['paid'] == False
        assert response.status_code == 200





    def test_cafeteria_order_with_discount(self):
        user1 = User.objects.get(username="user1")
        client = APIClient()
        client.force_authenticate(user=user1)

        #user1 has 0 cafeteria orders
        response = client.get('/api/cafeteriaOrders/')
        assert response.data['count'] == 0
        # and 0 vouchers
        response = client.get('/api/cafeteriaVouchers/')
        assert response.data['count'] == 0


        #buying one ticket for performance 1 to have 4 vouchers in wich 3 are discount 5
        jsonData = {}
        jsonData['performanceID'] = 1
        jsonData['numberOfTickets'] = 1
        jsonData['signature'] = "assinaturaTesteDebugPurpose"
        response = client.post('/api/buyTickets', jsonData, format='json')
        # now he has 4 vouchers and 3 are 5% discount
        response = client.get('/api/cafeteriaVouchers/')
        assert response.data['count'] == 4
        assert response.data['results'][0]['type'] == CafeteriaVoucher.DISCOUNT_5
        assert response.data['results'][1]['type'] == CafeteriaVoucher.DISCOUNT_5


        #performance doesnt exist
        jsonData = {}
        jsonData['voucher1ID'] = 1
        jsonData['voucher2ID'] = -1
        jsonData['coffees_quantity'] = 1
        jsonData['popcorn_quantity'] = 1
        jsonData['soda_quantity'] = 1
        jsonData['sandwich_quantity'] = 1
        jsonData['signature'] = "assinaturaTesteDebugPurpose"
        response = client.post('/api/cafeteriaOrders/', jsonData, format='json')
        assert response.data['priceToPay'] == (WebService.views.COFFEE_PRICE + WebService.views.SODA_PRICE + WebService.views.POPCORN_PRICE + WebService.views.SANDWICH_PRICE)*0.95

        #should have one not paid order
        response = client.get('/api/cafeteriaOrders/')
        assert response.data['count'] == 1
        assert response.data['results'][0]['paid'] == False
        assert response.status_code == 200







    def test_pay_cafeteria_order(self):
        user1 = User.objects.get(username="user1")
        client = APIClient()
        client.force_authenticate(user=user1)

        #user1 has 0 cafeteria orders
        response = client.get('/api/cafeteriaOrders/')
        assert response.data['count'] == 0
        # and 0 vouchers
        response = client.get('/api/cafeteriaVouchers/')
        assert response.data['count'] == 0


        #error with the post
        jsonData = {}
        response = client.post('/api/payCafeteriaOrder', jsonData, format='json')
        assert response.status_code == 400
        assert response.data['errorMsg'] == "Error reading order"

        #order doesnt exist
        jsonData = {}
        jsonData['orderID'] = 1
        jsonData['userID'] = user1.id
        jsonData['signature'] = "assinaturaTesteDebugPurpose"
        response = client.post('/api/payCafeteriaOrder', jsonData, format='json')
        assert response.status_code == 400
        assert response.data['errorMsg'] == "Cant find that order"




        #make order without vouchers
        jsonData = {}
        jsonData['voucher1ID'] = -1
        jsonData['voucher2ID'] = -1
        jsonData['coffees_quantity'] = 1
        jsonData['popcorn_quantity'] = 1
        jsonData['soda_quantity'] = 1
        jsonData['sandwich_quantity'] = 1
        jsonData['signature'] = "assinaturaTesteDebugPurpose"
        response = client.post('/api/cafeteriaOrders/', jsonData, format='json')
        assert response.data['priceToPay'] == WebService.views.COFFEE_PRICE + WebService.views.SODA_PRICE + WebService.views.POPCORN_PRICE + WebService.views.SANDWICH_PRICE

        #should have one not paid order
        response = client.get('/api/cafeteriaOrders/')
        assert response.data['count'] == 1
        assert response.data['results'][0]['paid'] == False
        assert response.status_code == 200


        #pay the order
        jsonData = {}
        jsonData['orderID'] = 1
        jsonData['userID'] = user1.id
        jsonData['signature'] = "assinaturaTesteDebugPurpose"
        response = client.post('/api/payCafeteriaOrder', jsonData, format='json')
        assert response.status_code == 200
        assert response.data['pricePaid'] == WebService.views.COFFEE_PRICE + WebService.views.SODA_PRICE + WebService.views.POPCORN_PRICE + WebService.views.SANDWICH_PRICE

        #should have now been paid
        response = client.get('/api/cafeteriaOrders/')
        assert response.data['count'] == 1
        assert response.data['results'][0]['paid'] == True
        assert response.status_code == 200


