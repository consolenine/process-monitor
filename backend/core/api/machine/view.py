from django.db import models
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import status

from ...models import (
    Machine, MachineConfigSerializer, MachineListSerializer
)


class MachineViewSet(ModelViewSet):
    """
    ViewSet to manage agents
    """
    serializer_class = MachineConfigSerializer
    permission_classes = []
    lookup_field = "machine_id"

    def get_queryset(self):
        return Machine.objects.all()

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, machine_id=self.kwargs.get("machine_id"))
        self.check_object_permissions(self.request, obj)
        return obj

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = MachineListSerializer(queryset, many=True)
        return Response(serializer.data)