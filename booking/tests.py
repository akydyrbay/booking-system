from django.test import TestCase

# Create your tests here.

from django.contrib.auth.models import User
from django.urls import reverse
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
        self.user = User.objects.create_user(username="testuser", password="testpassword123")
        self.other_user = User.objects.create_user(username="other", password="password123")
        self.room = Room.objects.create(room="Room 1", price_per_night=100.00, capacity=2)
        
        response = self.client.post(reverse("login"), {"username": "testuser", "password": "testpassword123"})
        self.token = response.data["token"]
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)

    def test_create_booking(self):
        url = reverse("bookings-list")
        data = {
            "room": self.room.id,
            "start_date": "2024-07-01",
            "end_date": "2024-07-10",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_cancel_booking(self):
        booking = Booking.objects.create(
            user=self.user, room=self.room, 
            start_date="2024-07-01", end_date="2024-07-10"
        )
        url = reverse("bookings-detail", args=[booking.id])
        response = self.client.delete(url) 
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Booking.objects.count(), 0)

    def test_prevent_double_booking(self):
        """Logic check: Ensure overlapping bookings are rejected."""
        Booking.objects.create(
            user=self.user, room=self.room, 
            start_date="2024-07-01", end_date="2024-07-10"
        )
        url = reverse("bookings-list")
        data = {
            "room": self.room.id,
            "start_date": "2024-07-05", # Overlaps
            "end_date": "2024-07-15",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)