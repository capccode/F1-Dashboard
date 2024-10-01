# backend/f1dashboard_api/api/views.py

import fastf1
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Max, Avg, Sum, Min
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import PageNumberPagination
from .utils import fetch_telemetry_data, initialize_fastf1_cache
from .models import Telemetry, Driver, Team, GrandPrix, Session
from .serializers import (
    TelemetrySerializer,
    DriverSerializer,
    TeamSerializer,
    GrandPrixSerializer,
    SessionSerializer,
)


@api_view(['GET'])
def get_grand_prix_options(request):
    """
    Returns a list of Grand Prix events for a selected year.
    """
    year = request.query_params.get('year')

    if not year:
        return Response({"error": "Year parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        year = int(year)
        # Fetch the Grand Prix events using fastf1
        schedule = fastf1.get_event_schedule(year=year, include_testing=False)
        options = [
            {
                'id': int(event['RoundNumber']),
                'name': event['EventName'],
                'location': event['Location'],
                'country': event['Country'],
                'date': event['EventDate'].strftime('%Y-%m-%d'),
            }
            for _, event in schedule.iterrows()
        ]
        return Response(options, status=status.HTTP_200_OK)
    except ValueError:
        return Response({"error": "Year must be an integer."}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_session_options(request):
    """
    Returns a list of sessions for a selected Grand Prix.
    """
    year = request.query_params.get('year')
    grand_prix_id = request.query_params.get('grand_prix_id')

    if not all([year, grand_prix_id]):
        return Response(
            {"error": "Year and Grand Prix ID parameters are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        year = int(year)
        grand_prix_id = int(grand_prix_id)
        event = fastf1.get_event(year, grand_prix_id)
        sessions = ['FP1', 'FP2', 'FP3', 'Q', 'R']
        options = [{'name': session, 'type': session} for session in sessions]
        return Response(options, status=status.HTTP_200_OK)
    except ValueError:
        return Response(
            {"error": "Year and Grand Prix ID must be integers."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_driver_options(request):
    """
    Returns a list of drivers for a selected session.
    """
    year = request.query_params.get('year')
    grand_prix_id = request.query_params.get('grand_prix_id')
    session_type = request.query_params.get('session')

    if not all([year, grand_prix_id, session_type]):
        return Response(
            {"error": "Year, Grand Prix ID, and Session parameters are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        year = int(year)
        grand_prix_id = int(grand_prix_id)
        session = fastf1.get_session(year, grand_prix_id, session_type)
        session.load(telemetry=True)  # Ensure telemetry data is fully loaded
        drivers = session.laps['Driver'].unique()
        options = [{'code': driver, 'name': session.get_driver(driver)['FullName']} for driver in drivers]
        return Response(options, status=status.HTTP_200_OK)
    except ValueError:
        return Response({"error": "Invalid parameters."}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_lap_info(request):
    """
    Returns maximum lap number and lap marks for a selected session.
    """
    year = request.query_params.get('year')
    grand_prix_id = request.query_params.get('grand_prix_id')
    session_type = request.query_params.get('session')

    if not all([year, grand_prix_id, session_type]):
        return Response(
            {"error": "Year, Grand Prix ID, and Session parameters are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        year = int(year)
        grand_prix_id = int(grand_prix_id)
        session = fastf1.get_session(year, grand_prix_id, session_type)
        session.load(telemetry=True)  # Ensure telemetry data is fully loaded
        max_lap = int(session.laps['LapNumber'].max())
        lap_marks = {
            i: f"Lap {i}" for i in range(1, max_lap + 1) if i == 1 or i % 5 == 0 or i == max_lap
        }
        return Response({"max_lap": max_lap, "lap_marks": lap_marks}, status=status.HTTP_200_OK)
    except ValueError:
        return Response({"error": "Invalid parameters."}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_telemetry_data(request):
    """
    Fetches telemetry data dynamically using fetch_telemetry_data utility function.
    """
    required_params = ['year', 'grand_prix_id', 'session', 'driver', 'lap']
    missing_params = [param for param in required_params if not request.query_params.get(param)]
    
    if missing_params:
        return Response({"error": f"Missing required parameters: {', '.join(missing_params)}"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Initialize FastF1 cache
        initialize_fastf1_cache()

        # Fetch telemetry data
        data = fetch_telemetry_data(
            year=request.query_params.get('year'),
            grand_prix_id=request.query_params.get('grand_prix_id'),
            session_type=request.query_params.get('session'),
            drivers=request.query_params.getlist('driver'),
            lap=request.query_params.get('lap')
        )

        # Check if data was returned correctly
        if not data:
            return Response({"error": "No telemetry data found for the provided parameters."}, status=status.HTTP_404_NOT_FOUND)

        return Response(data, status=status.HTTP_200_OK)

    except ValueError as ve:
        return Response({"error": f"Invalid parameter error: {str(ve)}"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": f"Unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Existing class-based views

class TelemetryListView(generics.ListAPIView):
    """
    API endpoint that allows telemetry data to be viewed.
    Supports filtering by year, grand_prix, session, driver, and lap.
    """
    serializer_class = TelemetrySerializer
    queryset = Telemetry.objects.all()
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = [
        'session__grand_prix__year',
        'session__grand_prix__name',
        'session__session_type',
        'driver__code',
        'lap',
    ]
    ordering_fields = [
        'lap',
        'distance',
        'speed',
        'throttle',
        'brake',
        'gear',
        'rpm',
        'drs',
    ]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        """
        Optionally restricts the returned telemetry data to a given set of drivers,
        by filtering against a `driver` query parameter in the URL.
        """
        queryset = super().get_queryset()
        drivers = self.request.query_params.getlist('driver')  # Fetch multiple driver parameters
        if drivers:
            queryset = queryset.filter(driver__code__in=drivers)
        return queryset

    # If you want to use the utility function in TelemetryListView
    # You might need to override the `list` method
    def list(self, request, *args, **kwargs):
        year = request.query_params.get('year')
        grand_prix_id = request.query_params.get('grand_prix_id')
        session_type = request.query_params.get('session')
        drivers = request.query_params.getlist('driver')
        lap = request.query_params.get('lap')

        if not all([year, grand_prix_id, session_type, drivers, lap]):
            return Response({"error": "All parameters are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            data = fetch_telemetry_data(year, grand_prix_id, session_type, drivers, lap)
            return Response(data, status=status.HTTP_200_OK)
        except ValueError as ve:
            return Response({"error": f"Invalid parameters: {str(ve)}"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Unexpected error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Other existing views (DriverListView, GrandPrixListView, etc.)

class DriverListView(generics.ListAPIView):
    """
    API endpoint that allows drivers to be viewed.
    """
    serializer_class = DriverSerializer
    queryset = Driver.objects.all()
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['team__name', 'code', 'name']
    ordering_fields = ['name', 'code']
    pagination_class = PageNumberPagination

class GrandPrixListView(generics.ListAPIView):
    """
    API endpoint that allows Grand Prix events to be viewed.
    """
    serializer_class = GrandPrixSerializer
    queryset = GrandPrix.objects.all()
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['year', 'name', 'location', 'date']
    ordering_fields = ['date', 'name']
    pagination_class = PageNumberPagination

class SessionListView(generics.ListAPIView):
    """
    API endpoint that allows sessions to be viewed.
    """
    serializer_class = SessionSerializer
    queryset = Session.objects.all()
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['grand_prix__name', 'session_type']
    ordering_fields = ['grand_prix__name', 'session_type', 'start_time']
    pagination_class = PageNumberPagination

from rest_framework.views import APIView  # Ensure this is imported

class AggregateTelemetryView(APIView):
    """
    API endpoint that provides aggregate telemetry data, such as average speed per lap.
    """
    def get(self, request, format=None):
        year = request.query_params.get('year')
        grand_prix = request.query_params.get('grand_prix')
        session = request.query_params.get('session')
        driver = request.query_params.get('driver')
        lap = request.query_params.get('lap')

        if not all([year, grand_prix, session, driver, lap]):
            return Response(
                {"error": "Missing required query parameters."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            telemetry = Telemetry.objects.filter(
                session__grand_prix__year=year,
                session__grand_prix__name=grand_prix,
                session__session_type=session,
                driver__code=driver,
                lap=lap,
            )

            if not telemetry.exists():
                return Response(
                    {"error": "No telemetry data found for the provided parameters."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Use Avg, Max, Sum directly without 'models.' prefix
            average_speed = telemetry.aggregate(avg_speed=Avg('speed'))['avg_speed']

            return Response({"average_speed": average_speed}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"Unexpected error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TelemetryStatsView(generics.GenericAPIView):
    """
    API endpoint that provides statistical data for telemetry.
    """
    serializer_class = TelemetrySerializer  # Or a different serializer if needed

    def get(self, request, *args, **kwargs):
        year = request.query_params.get('year')
        grand_prix = request.query_params.get('grand_prix')
        session = request.query_params.get('session')
        driver = request.query_params.get('driver')
        lap = request.query_params.get('lap')

        if not all([year, grand_prix, session, driver, lap]):
            return Response(
                {"error": "Missing required query parameters."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            telemetry = Telemetry.objects.filter(
                session__grand_prix__year=year,
                session__grand_prix__name=grand_prix,
                session__session_type=session,
                driver__code=driver,
                lap=lap,
            )

            if not telemetry.exists():
                return Response(
                    {"error": "No telemetry data found for the provided parameters."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Use Avg, Max, Sum directly
            stats = telemetry.aggregate(
                avg_speed=Avg('speed'),
                max_speed=Max('speed'),
                min_speed=Min('speed'),
                total_throttle=Sum('throttle'),
                total_brake=Sum('brake'),
                # Add more aggregations as needed
            )

            return Response(stats, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"Unexpected error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
