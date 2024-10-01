# backend/f1dashboard_api/api/urls.py

from django.urls import path
from .views import (
    TelemetryListView,
    AggregateTelemetryView,
    TelemetryStatsView,
    DriverListView,
    GrandPrixListView,
    SessionListView,
    get_grand_prix_options,
    get_session_options,
    get_driver_options,
    get_lap_info,
    get_telemetry_data,
)

urlpatterns = [
    path('telemetry/', TelemetryListView.as_view(), name='telemetry-list'),
    path('telemetry/aggregate/', AggregateTelemetryView.as_view(), name='telemetry-aggregate'),
    path('telemetry/stats/', TelemetryStatsView.as_view(), name='telemetry-stats'),
    path('drivers/', DriverListView.as_view(), name='driver-list'),
    path('grand-prix/', GrandPrixListView.as_view(), name='grand-prix-list'),
    path('sessions/', SessionListView.as_view(), name='session-list'),
    # New endpoints
    path('grand_prix_options/', get_grand_prix_options, name='grand_prix_options'),
    path('session_options/', get_session_options, name='session_options'),
    path('driver_options/', get_driver_options, name='driver_options'),
    path('lap_info/', get_lap_info, name='lap_info'),
    path('telemetry_data/', get_telemetry_data, name='telemetry_data'),
]
