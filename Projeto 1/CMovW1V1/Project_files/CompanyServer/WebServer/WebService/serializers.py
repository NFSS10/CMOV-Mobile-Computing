from WebService.models import User, Performance, Ticket, CafeteriaVoucher, CafeteriaOrder
from rest_framework import serializers



class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'first_name', 'last_name', 'nif','creditcard_number', 'cc_type', 'cc_validity', 'public_key')



class PerformanceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Performance
        fields = ('id', 'name', 'startDate', 'price')



class TicketSerializer(serializers.HyperlinkedModelSerializer):
    performance = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    user = serializers.PrimaryKeyRelatedField(many=False, read_only=True)

    class Meta:
        model = Ticket
        fields = ('id', 'used', 'place', 'performance', 'user', 'created_at')



class CafeteriaVoucherSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.PrimaryKeyRelatedField(many=False, read_only=True)

    class Meta:
        model = CafeteriaVoucher
        fields = ('id', 'used', 'user', 'type')



class CafeteriaOrderSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.PrimaryKeyRelatedField(many=False, read_only=True)

    class Meta:
        model = CafeteriaOrder
        fields = ('id', 'paid', 'voucher1ID', 'voucher2ID', 'user', 'coffees_quantity', 'popcorn_quantity', 'soda_quantity', 'sandwich_quantity', 'price')