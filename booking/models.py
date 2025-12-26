from django.db import models

# Create your models here.

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone


class Room(models.Model):
    room = models.CharField(max_length=100, unique=True)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.IntegerField()

    def __str__(self) -> str:
        return self.room if self.room is not None else ""


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    is_canceled = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.room} - {self.user}"

    def save(self, *args, **kwargs) -> None:
        if self.start_date < timezone.now().date():
            raise ValidationError("Start date cannot be in the past.")
        if self.end_date < self.start_date:
            raise ValidationError("The end date cannot be earlier than the start date.")

        # Check for conflicts, but only with bookings that aren't canceled
        conflicting_bookings = Booking.objects.filter(
            room=self.room,
            start_date__lte=self.end_date,
            end_date__gte=self.start_date,
            is_canceled=False,
        ).exclude(pk=self.pk)

        if conflicting_bookings.exists():
            raise ValidationError(
                "This room is already booked for the specified period."
            )
        super().save(*args, **kwargs)
