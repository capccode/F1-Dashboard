# backend/f1dashboard_api/api/admin.py

from django.contrib import admin
from .models import Team, Driver, GrandPrix, Session, Telemetry

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'base', 'principal', 'constructor_number')
    search_fields = ('name', 'base', 'principal')

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'team')
    list_filter = ('team',)
    search_fields = ('code', 'name')

@admin.register(GrandPrix)
class GrandPrixAdmin(admin.ModelAdmin):
    list_display = ('name', 'year', 'location', 'country', 'date')
    list_filter = ('year', 'country')
    search_fields = ('name', 'location')

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('grand_prix', 'session_type', 'start_time')
    list_filter = ('grand_prix', 'session_type')
    search_fields = ('grand_prix__name', 'session_type')

@admin.register(Telemetry)
class TelemetryAdmin(admin.ModelAdmin):
    list_display = ('driver', 'session', 'lap', 'distance', 'speed', 'throttle', 'brake', 'gear', 'rpm', 'drs')
    list_filter = ('session__grand_prix', 'session__session_type', 'driver')
    search_fields = ('driver__name', 'session__grand_prix__name')