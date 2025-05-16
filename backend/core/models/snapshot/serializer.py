from rest_framework import serializers
from .model import MachineSnapshot, ProcessSnapshot, SnapshotBatch
from ..machine import Machine

class MachineSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = MachineSnapshot
        exclude = ['batch']  # Will be linked via parent serializer


class ProcessSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessSnapshot
        exclude = ['batch']


class SnapshotBatchSerializer(serializers.ModelSerializer):
    machine_snapshot = MachineSnapshotSerializer()
    processes = ProcessSnapshotSerializer(many=True)
    machine_id = serializers.CharField(write_only=True)

    class Meta:
        model = SnapshotBatch
        fields = ["machine_id", "timestamp", "machine_snapshot", "processes"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        include_process_tree = self.context.get('include_process_tree', "1")
        if include_process_tree == "0":
            self.fields.pop('processes')

    def create(self, validated_data):
        machine_id = validated_data.pop("machine_id")
        machine_snapshot_data = validated_data.pop("machine_snapshot")
        process_data = validated_data.pop("processes")

        try:
            machine = Machine.objects.get(machine_id=machine_id)
        except Machine.DoesNotExist:
            raise serializers.ValidationError(f"Machine with ID '{machine_id}' not found.")

        snapshot_batch = SnapshotBatch.objects.create(machine=machine)

        # Create machine snapshot
        MachineSnapshot.objects.create(batch=snapshot_batch, **machine_snapshot_data)

        # Create all process snapshots
        for process in process_data:
            ProcessSnapshot.objects.create(batch=snapshot_batch, **process)

        return snapshot_batch
