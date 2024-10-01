# backend/f1dashboard_api/api/models.py

from django.db import models

class Team(models.Model):
    """
    Represents an F1 team.
    """
    name = models.CharField(max_length=100, unique=True)
    base = models.CharField(max_length=100, blank=True, null=True)  # Base location of the team
    principal = models.CharField(max_length=100, blank=True, null=True)  # Team principal's name
    constructor_number = models.IntegerField(unique=True)  # Unique constructor number

    def __str__(self):
        return self.name

class Driver(models.Model):
    """
    Represents an F1 driver.
    """
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=50)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='drivers')

    def __str__(self):
        return f"{self.name} ({self.code})"

class GrandPrix(models.Model):
    """
    Represents an F1 Grand Prix event.
    """
    name = models.CharField(max_length=100)
    year = models.IntegerField()
    location = models.CharField(max_length=100, blank=True, null=True)  # City or circuit location
    country = models.CharField(max_length=50, blank=True, null=True)
    date = models.DateField()

    class Meta:
        unique_together = ('name', 'year')

    def __str__(self):
        return f"{self.name} {self.year}"

class Session(models.Model):
    """
    Represents a specific session within a Grand Prix (e.g., FP1, Q, R).
    """
    SESSION_TYPES = [
        ('FP1', 'Free Practice 1'),
        ('FP2', 'Free Practice 2'),
        ('FP3', 'Free Practice 3'),
        ('Q', 'Qualifying'),
        ('R', 'Race'),
    ]

    session_type = models.CharField(max_length=3, choices=SESSION_TYPES)
    grand_prix = models.ForeignKey(GrandPrix, on_delete=models.CASCADE, related_name='sessions')
    start_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ('session_type', 'grand_prix')
        ordering = ['start_time']

    def __str__(self):
        return f"{self.grand_prix.name} {self.grand_prix.year} - {self.get_session_type_display()}"

class Telemetry(models.Model):
    """
    Represents telemetry data for a driver during a specific lap at a specific distance.
    """
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='telemetries')
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='telemetries')
    lap = models.IntegerField()
    distance = models.FloatField(help_text="Distance covered in meters")
    speed = models.FloatField(help_text="Speed in km/h")
    throttle = models.FloatField(help_text="Throttle percentage")
    brake = models.FloatField(help_text="Brake percentage")
    gear = models.IntegerField(help_text="Current gear")
    rpm = models.IntegerField(help_text="Engine RPM")
    drs = models.BooleanField(help_text="DRS active status")

    class Meta:
        unique_together = ('session', 'driver', 'lap', 'distance')
        ordering = ['session', 'driver', 'lap', 'distance']

    def __str__(self):
        return f"{self.driver.code} - {self.session} Lap {self.lap} Distance {self.distance}"