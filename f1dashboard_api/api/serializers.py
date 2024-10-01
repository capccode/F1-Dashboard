# backend/f1dashboard_api/api/serializers.py

from rest_framework import serializers
from .models import Telemetry, Driver, Team, GrandPrix, Session

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['id', 'name', 'base', 'principal', 'constructor_number']
        # Removed 'color' field as it doesn't exist in the Team model

class DriverSerializer(serializers.ModelSerializer):
    team = TeamSerializer(read_only=True)
    nationality = serializers.CharField(source='nationality', read_only=True)  # Added nationality field

    class Meta:
        model = Driver
        fields = ['id', 'code', 'name', 'team', 'nationality']  # Included nationality field

class GrandPrixSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrandPrix
        fields = ['id', 'name', 'year', 'location', 'country', 'date']
        # Removed 'circuit_length' and 'laps' fields as they don't exist in the GrandPrix model

class SessionSerializer(serializers.ModelSerializer):
    grand_prix = GrandPrixSerializer(read_only=True)
    weather = serializers.CharField(source='weather', read_only=True)  # Added weather field

    class Meta:
        model = Session
        fields = ['id', 'grand_prix', 'session_type', 'start_time', 'weather']  # Included weather field

class TelemetrySerializer(serializers.ModelSerializer):
    driver = DriverSerializer(read_only=True)
    session = SessionSerializer(read_only=True)
    x = serializers.FloatField(read_only=True)  # Added x coordinate field
    y = serializers.FloatField(read_only=True)  # Added y coordinate field
    z = serializers.FloatField(read_only=True)  # Added z coordinate field
    delta_time = serializers.FloatField(read_only=True)  # Added delta time field

    class Meta:
        model = Telemetry
        fields = [
            'id',
            'driver',
            'session',
            'lap',
            'distance',
            'speed',
            'throttle',
            'brake',
            'gear',
            'rpm',
            'drs',
            'x',  # Added x coordinate field
            'y',  # Added y coordinate field
            'z',  # Added z coordinate field
            'delta_time',  # Added delta time field
        ]
