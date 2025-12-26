# Create your tests here.

from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Booking, Room


class UserRegistrationTests(APITestCase):
    def test_register_user(self):
        url = reverse("register")
        data = {
            "username": "testuser",
            "password": "testpassword123",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, "testuser")


class UserLoginTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword123",
        )

    def test_login_user(self):
        url = reverse("login")
        data = {
            "username": "testuser",
            "password": "testpassword123",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)
        self.token = response.data["token"]


class RoomTests(APITestCase):
    def setUp(self):
        Room.objects.create(room="Room 1", price_per_night=100.00, capacity=2)
        Room.objects.create(room="Room 2", price_per_night=150.00, capacity=3)

    def test_view_rooms(self):
        url = reverse("rooms-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)


class BookingTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword123"
        )
        self.other_user = User.objects.create_user(
            username="other", password="password123"
        )
        self.room = Room.objects.create(
            room="Room 1", price_per_night=100.00, capacity=2
        )

        response = self.client.post(
            reverse("login"), {"username": "testuser", "password": "testpassword123"}
        )
        self.token = response.data["token"]
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)

    def test_create_booking(self):
        url = reverse("bookings-list")
        start_date = (timezone.now() + timedelta(days=1)).date()
        end_date = (timezone.now() + timedelta(days=5)).date()
        data = {
            "room": self.room.id,
            "start_date": str(start_date),
            "end_date": str(end_date),
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_cancel_booking(self):
        start_date = (timezone.now() + timedelta(days=1)).date()
        end_date = (timezone.now() + timedelta(days=5)).date()
        booking = Booking.objects.create(
            user=self.user, room=self.room, start_date=start_date, end_date=end_date
        )
        url = reverse("bookings-detail", args=[booking.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verify booking is marked as canceled, not deleted
        booking.refresh_from_db()
        self.assertTrue(booking.is_canceled)

    def test_prevent_double_booking(self):
        """Logic check: Ensure overlapping bookings are rejected."""
        start_date = (timezone.now() + timedelta(days=1)).date()
        end_date = (timezone.now() + timedelta(days=10)).date()
        Booking.objects.create(
            user=self.user, room=self.room, start_date=start_date, end_date=end_date
        )
        url = reverse("bookings-list")
        overlap_start = (timezone.now() + timedelta(days=5)).date()
        overlap_end = (timezone.now() + timedelta(days=15)).date()
        data = {
            "room": self.room.id,
            "start_date": str(overlap_start),
            "end_date": str(overlap_end),
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
