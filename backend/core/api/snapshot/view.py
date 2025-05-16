from rest_framework import viewsets, filters
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from datetime import timedelta
from django_filters.rest_framework import DjangoFilterBackend
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from ...models import (
    ProcessSnapshot,
    SnapshotBatch,
    SnapshotBatchSerializer,
    MachineSnapshotSerializer,
)
from ...utils import build_process_tree, apply_time_range_filter

class SnapshotBatchPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 500

class SnapshotBatchViewSet(viewsets.ModelViewSet):
    serializer_class = SnapshotBatchSerializer
    pagination_class = SnapshotBatchPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["machine__machine_id", "machine__hostname", "timestamp"]
    ordering_fields = ["timestamp"]

    def get_queryset(self):
        return SnapshotBatch.objects.prefetch_related("machine_snapshot", "processes")

    def list(self, request, *args, **kwargs):
        machine_id = request.query_params.get("machine_id")
        time_range = request.query_params.get("since")  # e.g., "30m", "1h", "3h", "1d"
        include_process_tree = request.query_params.get("include_process_tree", "1") # 1 == True; 0 == False
        qs = self.get_queryset()

        if not machine_id:
            return Response([])  # Return empty list if machine_id not provided

        qs = qs.filter(machine__machine_id=machine_id)

        # Time range filtering
        if time_range:
            qs = apply_time_range_filter(qs, time_range)

        qs = qs.order_by("-timestamp")

        # Return only latest if no time_range specified
        if not time_range:
            qs = qs[:1]

        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True, context={'include_process_tree': include_process_tree})
            data = serializer.data

            for batch in data:
                flat_processes = batch.pop("processes", [])
                batch["process_tree"] = build_process_tree(flat_processes)

            return self.get_paginated_response(data)

        serializer = self.get_serializer(qs, many=True)
        data = serializer.data

        for batch in data:
            flat_processes = batch.pop("processes", [])
            batch["process_tree"] = build_process_tree(flat_processes)

        return Response(data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        snapshot_batch = serializer.save()

        # After save: safely broadcast
        machine_id = snapshot_batch.machine.machine_id
        machine_snapshot = snapshot_batch.machine_snapshot
        machine_snapshot_data = (
            MachineSnapshotSerializer(machine_snapshot).data if machine_snapshot else {}
        )
        processes = ProcessSnapshot.objects.filter(batch=snapshot_batch).values(
            "pid", "ppid", "name", "cpu_usage", "memory_usage"
        )
        process_tree = build_process_tree(list(processes))

        payload = {
            "timestamp": snapshot_batch.timestamp.isoformat(),
            "machine_id": machine_id,
            "machine_snapshot": machine_snapshot_data,
            "process_tree": process_tree,
        }

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"machine_{machine_id}",
            {
                "type": "snapshot_message",
                "message": payload,
            }
        )

        return Response(data={"status": "success"}, status=status.HTTP_201_CREATED)