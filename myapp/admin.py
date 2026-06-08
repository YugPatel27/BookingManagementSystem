from django.contrib import admin
from .models import catagory, movie, cinemas, BookingEvents, seat_layout, payment_details, otp, SeatType, events, seat_layout_movie, booking_details

# Register your models here.
admin.site.register(catagory)
admin.site.register(movie)
admin.site.register(cinemas)
admin.site.register(seat_layout)
admin.site.register(payment_details)
admin.site.register(otp)
admin.site.register(SeatType)
admin.site.register(events)
admin.site.register(BookingEvents)
admin.site.register(seat_layout_movie)
admin.site.register(booking_details)