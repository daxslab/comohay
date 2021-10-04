from rest_framework import serializers


class ClassifiedsPlatformSerializer(serializers.Serializer):

    name = serializers.CharField()
    url = serializers.URLField()

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass