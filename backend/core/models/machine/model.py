from django.db import models


class Machine(models.Model):
    """
    Represents a machine that is being monitored.
    """
    hostname = models.CharField(max_length=255, unique=True)
    machine_id = models.CharField(max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Agent Config
    polling_interval = models.PositiveIntegerField(default=5)  # in seconds
    enabled = models.BooleanField(default=True)

    # Machine Specification
    os_name = models.CharField(max_length=100)
    architecture = models.CharField(max_length=100)
    processor = models.CharField(max_length=200)
    cpu_cores = models.IntegerField()
    cpu_threads = models.IntegerField()
    total_ram = models.IntegerField()
    total_storage = models.IntegerField()

    def __str__(self):
        return self.hostname