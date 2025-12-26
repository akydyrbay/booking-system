from django.shortcuts import render

# Create your views here.

from django.contrib.auth.models import User
from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .filters import RoomFilter
from .models import Booking, Room
from .serializers import BookingSerializer, RegisterSerializer, RoomSerializer


class RoomViewSet(ReadOnlyModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = RoomFilter
    ordering_fields = ["price_per_night", "capacity"]
    ordering = ["price_per_night"]
    permission_classes = [IsAuthenticatedOrReadOnly]


class BookingViewSet(ModelViewSet):
    serializer_class = BookingSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> QuerySet:
        if self.request.user.is_superuser:
            return Booking.objects.all()
        return Booking.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        start_date = serializer.validated_data["start_date"]
        end_date = serializer.validated_data["end_date"]
        room_obj = serializer.validated_data["room"] 

        conflicting_bookings = Booking.objects.filter(
            room=room_obj, 
            start_date__lte=end_date,
            end_date__gte=start_date
        )

        if conflicting_bookings.exists():
            return Response(
                {"error": "The room is not available for the selected dates."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            booking = Booking.objects.create(
                user=request.user,
                room=room_obj,
                start_date=start_date,
                end_date=end_date
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        booking.save()

        return Response(
            {
                "message": "Room booked successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )

    def destroy(self, request, *args, **kwargs):
        try:
            booking = self.get_object()
        except Exception: 
            return Response({"error": "Booking not found"}, status=status.HTTP_404_NOT_FOUND)

        if request.user == booking.user or request.user.is_superuser:
            booking.delete()
            return Response(
                {"message": "Booking cancelled successfully."},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "You do not have permission to cancel this booking."},
                status=status.HTTP_403_FORBIDDEN,
            )

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]