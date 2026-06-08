from email.policy import default
from django.db import models

class catagory(models.Model):
    catagory_id = models.AutoField(primary_key=True)
    catagory_name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.catagory_name
    class Meta:
        db_table = 'catagory'

# class Email(models.Model):
#     email_id = models.EmailField()

class movie(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    release_date = models.DateField()
    ends_date = models.DateField(default=None, blank=True, null=True)
    genre = models.CharField(max_length=100)
    rating = models.DecimalField(max_digits=3, decimal_places=1)
    director = models.CharField(max_length=100)
    cast = models.CharField(max_length=100)
    movie_image = models.ImageField(upload_to='movies/', blank=True, null=True)
    duration = models.IntegerField(default=120, blank=True, null=True)
    language = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'movie'
class cinemas(models.Model):
    cinema_id = models.AutoField(primary_key=True)
    cinema_name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    screen_no = models.IntegerField(default=1)
    total_seats = models.IntegerField()

    show_timings = models.CharField(
        max_length=150,
        help_text="Comma separated show timings",
        default="10:00 AM,1:00 PM,4:00 PM,7:00 PM,10:00 PM"
    )

    movie_id = models.ForeignKey(movie, on_delete=models.CASCADE, related_name="cinemas" , default=1)

    class Meta:
        db_table = 'cinemas'

    def __str__(self):
        return f"{self.cinema_name} - Screen {self.screen_no}"

    # Return show timings as list
    def get_show_timings_list(self):
        return [t.strip() for t in self.show_timings.split(',')]

    #  Check if booking is allowed (no past shows)
    def is_booking_allowed(self, show_time):
        from datetime import datetime, time 
        today_time = datetime.now()
        now = datetime.strptime(show_time, "%H:%M").time()
        return today_time >= now.time()        
    
class payment_details(models.Model):
    booking_id = models.AutoField(primary_key=True)
    class Meta:
        db_table = 'payment_details'
    def __str__(self):
        return str(self.booking_id)

class otp(models.Model):
    otp = models.IntegerField()
    class Meta:
        db_table = 'otp'
    def __str__(self):
        return str(self.otp)


class events(models.Model):
    CATEGORY_CHOICES = [
        ('Music', 'Music'),
        ('Dance', 'Dance'),
        ('Theater', 'Theater'),
        ('Comedy', 'Comedy'),
        ('Sports', 'Sports'),
        ('workshop', 'Workshop'),
        ('exhibition', 'Exhibition'),
        ('other', 'Other'),
    ]

    LANGUAGE_CHOICES = [
        ('English', 'English'),
        ('Hindi', 'Hindi'),
        ('Kannada', 'Kannada'),
        ('Tamil', 'Tamil'),
        ('Telugu', 'Telugu'),
        ('Malayalam', 'Malayalam'),
        ('Bengali', 'Bengali'),
        ('Gujarati', 'Gujarati'),
        ('Marathi', 'Marathi'),
        ('Punjabi', 'Punjabi'),
        ('Odia', 'Odia'),
        ('Assamese', 'Assamese'),
        ('Urdu', 'Urdu'),
    ]
    event_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    venue = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    languages = models.CharField(max_length=50, choices=LANGUAGE_CHOICES)
    description = models.TextField()
    event_date = models.DateField()
    event_time = models.TimeField()
    duration = models.CharField(max_length=50)
    AgeLimit = models.CharField(max_length=20)
    image = models.ImageField(upload_to='events/',blank=True, null=True)
    artist_name = models.CharField(max_length=100)
    artist_picture = models.ImageField(upload_to='artists/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'events'
    def __str__(self):
        return self.title
class seat_layout_movie(models.Model):
    seat_layout_id = models.AutoField(primary_key=True)

    cinema = models.OneToOneField(
        cinemas,
        on_delete=models.CASCADE,
        related_name="seat_layout_movie"
    )

    gold = models.IntegerField()
    silver = models.IntegerField()
    platinum = models.IntegerField()

    class Meta:
        db_table = 'seat_layout_movie'

    def __str__(self):
        return f"{self.cinema} Seat Layout"
class SeatType(models.Model):
    event = models.ForeignKey(events, on_delete=models.CASCADE, related_name='seats')
    seat_name = models.CharField(max_length=100)
    seat_price = models.PositiveIntegerField()
    seat_total = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.seat_name} - {self.event.title}"

class BookingEvents(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    name = models.CharField(max_length=100)
    email_id = models.EmailField()
    B_date = models.DateField()
    
    phone_number = models.CharField(max_length=15)
    seat_catagory = models.CharField(max_length=100) # Kept 'catagory'

    Event = models.ForeignKey(events, on_delete=models.CASCADE)

    no_of_seats = models.IntegerField()
    total_amount = models.IntegerField()
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'booking_events'
       
    def __str__(self):
        return f"{self.name} - {self.Event.title}"

class Payment(models.Model):
    stripe_session_id = models.CharField(max_length=255, unique=True)
    amount = models.IntegerField()  # in cents
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    email = models.EmailField(blank=True, null=True)
 
    class Meta:
        db_table = 'payment'
   
    def __str__(self):
        return f"{self.stripe_session_id} - {self. Status}"
    
class booking_details(models.Model):
    name = models.CharField(max_length=100)
    email_id = models.EmailField()
    phone_number = models.IntegerField(default=0)
    birth_date = models.DateField()

    booking_time = models.DateTimeField(auto_now_add=True)

    seat_category = models.CharField(max_length=100, default='Gold')
    no_of_tickets = models.IntegerField()

    price_per_ticket = models.IntegerField()
    total_amount = models.IntegerField(default=0)

    cinema_id = models.ForeignKey(cinemas, on_delete=models.CASCADE)
    movie_id = models.ForeignKey(movie, on_delete=models.CASCADE,default=1)
    
    # Additional fields for movie details
    show_time = models.CharField(max_length=10, default="", blank=True, null=True)
    release_date = models.CharField(max_length=100, default="", blank=True, null=True)
    director = models.CharField(max_length=100, default="", blank=True, null=True)
    cast = models.CharField(max_length=255, default="", blank=True, null=True)
    screen_no = models.IntegerField(default=0, blank=True, null=True)
    
    # Order status tracking
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    class Meta:
        db_table = 'booking_details'
    
    def __str__(self):
        return f"{self.name} - {self.movie_id.name}"

class Offer(models.Model):
    movie = models.ForeignKey(movie, on_delete=models.CASCADE, related_name='offers')
    title = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return f"{self.title} - {self.movie.name}"






class Event_Price(models.Model):
    event_id = models.ForeignKey(events, on_delete=models.CASCADE)
    price = models.IntegerField()
    class Meta:
        db_table = 'event_price'
    def __str__(self):
        return str(self.event_id)






class seat_layout(models.Model):
    seat_layout_id = models.AutoField(primary_key=True)

    cinema = models.OneToOneField(
        cinemas,
        on_delete=models.CASCADE,
        related_name="seat_layout",
        default=1   
    )

    gold = models.IntegerField()
    silver = models.IntegerField()
    platinum = models.IntegerField()

    class Meta:
        db_table = 'seat_layout'

    def __str__(self):
        return f"{self.cinema} Seat Layout"


class OrderManagement(models.Model):
    """Track order/booking status and progression"""
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending Payment'),
        ('payment_received', 'Payment Received'),
        ('confirmed', 'Booking Confirmed'),
        ('completed', 'Booking Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    booking = models.OneToOneField(booking_details, on_delete=models.CASCADE, related_name='order')
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    payment_date = models.DateTimeField(null=True, blank=True)
    payment_method = models.CharField(max_length=50, default='Credit Card')
    
    class Meta:
        db_table = 'order_management'
    
    def __str__(self):
        return f"Order {self.id} - {self.booking.name} ({self.order_status})"


class Receipt(models.Model):
    """Store receipt information and PDF paths"""
    booking = models.OneToOneField(booking_details, on_delete=models.CASCADE, related_name='receipt')
    receipt_number = models.CharField(max_length=50, unique=True)
    pdf_path = models.CharField(max_length=255, null=True, blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'receipt'
    
    def __str__(self):
        return f"Receipt {self.receipt_number} - {self.booking.name}"


class UserProfile(models.Model):
    """Extended user profile for booking system"""
    from django.contrib.auth.models import User
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profile'
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}" if self.user.first_name else self.user.username