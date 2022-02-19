from rest_framework import serializers

class KhaltiCallbackSerializer(serializers.Serializer):
    idx = serializers.CharField()
    amount = serializers.IntegerField()
    mobile = serializers.CharField()
    product_identity = serializers.CharField()
    product_name = serializers.CharField()
    product_url = serializers.CharField()
    token = serializers.CharField()