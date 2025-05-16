from django.db import models

from ..machine import Machine


class SnapshotBatch(models.Model):
    """
    Represents a batch of snapshots taken from a machine.
    """
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name="batches")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.machine.hostname} - {self.timestamp}"

class MachineSnapshot(models.Model):
    batch = models.OneToOneField(SnapshotBatch, on_delete=models.CASCADE, related_name='machine_snapshot')
    timestamp = models.DateTimeField(auto_now_add=True)

    total_ram = models.BigIntegerField()
    used_ram = models.BigIntegerField()
    available_ram = models.BigIntegerField()

    total_disk = models.BigIntegerField()
    used_disk = models.BigIntegerField()
    available_disk = models.BigIntegerField()

    def __str__(self):
        return f"MachineSnapshot: {self.batch.machine.hostname} @ {self.timestamp}"


class ProcessSnapshot(models.Model):
    batch = models.ForeignKey(SnapshotBatch, on_delete=models.CASCADE, related_name="processes")
    pid = models.IntegerField()
    ppid = models.IntegerField()
    name = models.CharField(max_length=255)
    cpu_usage = models.FloatField()
    memory_usage = models.FloatField()

    def __str__(self):
        return f"{self.name} (PID: {self.pid})"