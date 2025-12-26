import datetime
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError

from booking.models import Booking, Room


class Command(BaseCommand):
    help = "Populates the database with initial data"

    def handle(self, *args, **options):
        User = get_user_model()

        if not User.objects.filter(username="admin123").exists():
            User.objects.create_superuser(
                username="admin123", email="admin@example.com", password="adminpass"
            )

        users = []
        for i in range(1, 4):
            username = f"user{i}"
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(username=username, password=f"pass{i}")
            else:
                user = User.objects.get(username=username)
            users.append(user)

        rooms = []
        for i in range(1, 11):
            room_name = f"Room {i}"
            room, _ = Room.objects.get_or_create(
                room=room_name,
                defaults={"price_per_night": 100.00 + i * 10, "capacity": 2 + i},
            )
            rooms.append(room)

        start_date = (timezone.now() + timedelta(days=1)).date()
        created = 0
        for i in range(30):
            user = users[i % len(users)]
            room = rooms[i % len(rooms)]
            end_date = start_date + datetime.timedelta(days=2)
            try:
                Booking.objects.create(user=user, room=room, start_date=start_date, end_date=end_date)
                created += 1
            except ValidationError:
                pass
            start_date += datetime.timedelta(days=1)

        self.stdout.write(self.style.SUCCESS(f"Created {len(users)} users, {len(rooms)} rooms, {created} bookings."))
