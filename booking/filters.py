import django_filters

from .models import Booking, Room


class RoomFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(
        field_name="price_per_night",
        lookup_expr="gte",
    )
    max_price = django_filters.NumberFilter(
        field_name="price_per_night",
        lookup_expr="lte",
    )
    min_capacity = django_filters.NumberFilter(
        field_name="capacity",
        lookup_expr="gte",
    )
    max_capacity = django_filters.NumberFilter(
        field_name="capacity",
        lookup_expr="lte",
    )

    class Meta:
        model = Room
        fields = [
            "min_price",
            "max_price",
            "min_capacity",
            "max_capacity",
        ]


class BookingFilter(django_filters.FilterSet):
    start_date = django_filters.DateFromToRangeFilter(field_name="start_date")
    end_date = django_filters.DateFromToRangeFilter(field_name="end_date")

    class Meta:
        model = Booking
        fields = {
            "room": ["exact"],
            "user": ["exact"],
            "start_date": ["gte", "lte"],
            "end_date": ["gte", "lte"],
            "is_canceled": ["exact"],
        }
