from rest_framework import serializers

from api.v1.serializers.ad import AdSerializer


class AdSearchSerializer(serializers.Serializer):
    title = serializers.CharField()
    highlight = serializers.SerializerMethodField()
    ad = serializers.SerializerMethodField()

    def get_highlight(self, obj):
        return obj.highlighted['text'][0]

    def get_ad(self, obj):
        return AdSerializer(obj.object).data
