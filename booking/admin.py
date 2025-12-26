from django.contrib import admin

# Register your models here.

from .models import Booking, Room


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("id", "room", "price_per_night", "capacity")

    list_display_links = ("id", "room")

    list_filter = ("capacity",)

    search_fields = ("room",)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "room", "start_date", "end_date")

    list_display_links = ("id", "user")

    list_filter = ("start_date", "end_date")

    search_fields = ("user__username", "room__room")
