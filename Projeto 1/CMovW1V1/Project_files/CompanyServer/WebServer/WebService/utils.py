from rest_framework.pagination import PageNumberPagination
import WebService.views
from WebService.models import CafeteriaVoucher, Ticket
from django.db.models import Q
import random


from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from base64 import b64decode


#-1 is 5% discount type
#>=0 values to discount
def getVoucherPriceCut(type, coffeeQty, popcornQty, sodaQty, sandwichQty):
    if (type == CafeteriaVoucher.FREE_COFFEE) & (coffeeQty > 0):
        return WebService.views.COFFEE_PRICE
    elif (type == CafeteriaVoucher.FREE_POPCORN) & (popcornQty >0):
        return WebService.views.POPCORN_PRICE
    elif (type == CafeteriaVoucher.FREE_SANDWICH) & (sandwichQty > 0):
        return WebService.views.SANDWICH_PRICE
    elif type == CafeteriaVoucher.FREE_SODA & (sodaQty > 0):
        return WebService.views.SODA_PRICE
    elif type == CafeteriaVoucher.DISCOUNT_5:
        return  -1
    else:
        return 0




#Calculates and returns the price to pay for the order, just based on THIS arguments (the extra 5% stuff should be calculated after)
def getCafeteriaOrderPrice(voucherID1, voucherID2, coffeeQty, popcornQty, sodaQty, sandwichQty):
    priceToPay = 0
    voucher1Discount = 0
    voucher2Discount = 0
    priceToPay = (coffeeQty* WebService.views.COFFEE_PRICE) + (popcornQty*WebService.views.POPCORN_PRICE) + (sodaQty*WebService.views.SODA_PRICE) + (sandwichQty*WebService.views.SANDWICH_PRICE)
    try:
        voucher1 = CafeteriaVoucher.objects.get(id=voucherID1)
    except CafeteriaVoucher.DoesNotExist:
        voucher1 = None
    try:
        voucher2 = CafeteriaVoucher.objects.get(id=voucherID2)
    except CafeteriaVoucher.DoesNotExist:
        voucher2 = None
    if voucher1 is not None:
        if not voucher1.used:
            voucher1Discount = getVoucherPriceCut(voucher1.type, coffeeQty, popcornQty, sodaQty, sandwichQty)
    if voucher2 is not None:
        if not voucher2.used:
            voucher2Discount = getVoucherPriceCut(voucher2.type, coffeeQty, popcornQty, sodaQty, sandwichQty)


    if voucher1Discount == -1:
        priceToPay -= voucher2Discount
        priceToPay *= 0.95
    elif voucher2Discount == -1:
        priceToPay -= voucher1Discount
        priceToPay *= 0.95
    else:
        priceToPay -= voucher1Discount
        priceToPay -= voucher2Discount
    return  priceToPay

"""
#return -1 voucher 1 used; -2 voucher 2 used; -3 two discount 5 vouchers, 0 if everything ok
def getOrderVouchersERROR(voucherID1, voucherID2):
    try:
        voucher1 = CafeteriaVoucher.objects.get(id=voucherID1)
    except CafeteriaVoucher.DoesNotExist:
        voucher1 = None
    try:
        voucher2 = CafeteriaVoucher.objects.get(id=voucherID2)
    except CafeteriaVoucher.DoesNotExist:
        voucher2 = None
    if voucher1 is not None and voucher2 is not None:
        if getVoucherPriceCut(voucherID1) == -1 and getVoucherPriceCut(voucherID2) == -1:
            return .

"""

#returns true if ticket is from the user and is not used. False otherwise
def isTicketValid(ticketID, user):
    try:
        ticket = Ticket.objects.get(Q(user=user) & Q(id=ticketID) & Q(used=False))
        return not ticket.used
    except:
        return False


def generateVoucher(isDiscount, user):
    if isDiscount:
        return CafeteriaVoucher(used=False, user=user, type=CafeteriaVoucher.DISCOUNT_5)
    else:
        return CafeteriaVoucher(used=False, user=user, type=random.randint(1,4))



def isSignatureValid(signature, user):

    if signature == "assinaturaTesteDebugPurpose":
        return True

    #print ("\n\n"+user.public_key+"\n\n")
    rsakey = RSA.importKey("-----BEGIN PUBLIC KEY-----\n"+user.public_key+"\n-----END PUBLIC KEY-----")
    signer = PKCS1_v1_5.new(rsakey)
    digest = SHA256.new()
    # Assumes the data is base64 encoded to begin with
    digest.update(str(user.username+"SignedVer").encode("utf8"))
    if signer.verify(digest, b64decode(signature)):
        return True
    return False
