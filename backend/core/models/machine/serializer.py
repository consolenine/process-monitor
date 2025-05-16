from rest_framework import serializers

from .model import Machine


class MachineConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = Machine
        exclude = ['id']

class MachineListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Machine
        fields = ["machine_id", "hostname"]

class MachineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Machine
        fields = '__all__'