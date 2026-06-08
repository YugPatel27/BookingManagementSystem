from PIL.TiffTags import DOUBLE
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
# Updated Import
from .models import catagory, movie, cinemas, seat_layout, payment_details, otp, SeatType, events, BookingEvents, booking_details, Payment
from datetime import datetime
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.db.models import Min
import stripe
from django.conf import settings
import json
import uuid
import os
from reportlab.pdfgen import canvas
from django.contrib.auth.models import User
from .models import UserProfile
stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

def index(request):
    return render(request, 'index.html')

def user_profile(request):
    return render(request, 'userprofile.html')

def user_favorite_list(request):
    return render(request, 'userfavoritelist.html')

def user_favorite_grid(request):
    return render(request, 'userfavoritegrid.html')

def user_rate(request):
    return render(request, 'userrate.html')


def movies_view(request): # Renamed to avoid name clash with 'movies' model
    return render(request, 'movielist.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            # Try to find user by email
            user = User.objects.get(email=email)
            # Authenticate with username
            user_auth = authenticate(request, username=user.username, password=password)
            
            if user_auth is not None:
                login(request, user_auth)
                messages.success(request, f"Welcome back, {user.first_name or user.username}!")
                return redirect('index')
            else:
                messages.error(request, "Invalid password. Please try again.")
                return render(request, 'index.html')
        except User.DoesNotExist:
            messages.error(request, "Email not found. Please sign up first.")
            return render(request, 'index.html')
    else:
        return render(request, 'index.html')

def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "You have been logged out successfully.")
    else:
        messages.info(request, "You are not logged in.")
    return redirect('index')

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        phone_number = request.POST.get('phone_number')
        date_of_birth = request.POST.get('date_of_birth')

        # Validation
        if not all([username, email, password, confirm_password]):
            messages.error(request, "Username, email, and password are required")
            return render(request, 'index.html')
        
        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return render(request, 'index.html')
        
        if len(password) < 6:
            messages.error(request, "Password must be at least 6 characters")
            return render(request, 'index.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return render(request, 'index.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return render(request, 'index.html')

        try:
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            # Create linked UserProfile with additional data
            UserProfile.objects.create(
                user=user,
                phone_number=phone_number,
                date_of_birth=date_of_birth if date_of_birth else None
            )

            # Auto login after registration
            login(request, user)
            messages.success(request, f"Welcome {first_name}! Your account has been created successfully.")
            return redirect('index')
        except Exception as e:
            messages.error(request, f"Error creating account: {str(e)}")
            return render(request, 'index.html')

    return render(request, 'index.html')

def home(request):
    return index(request)

def event(request):
    return render(request, 'index.html')

def eventlist(request):
    return render(request, 'index.html')

def eventsingle(request):
    return render(request, 'index.html')

def booking_single(request):
    return render(request, 'booking_single.html')
def booking_events_view(request):
    print("--------------------------------------------", request.POST.get('event_id'))
   
    if request.method == 'POST':
        try:
            event_id = request.POST.get('event_id')
            name = request.POST.get('name')
            email_id = request.POST.get('email_id')
            B_date = request.POST.get('B_date')
            phone_number = request.POST.get('phone_number')
            seat_catagory = request.POST.get('seat_catagory') # Kept 'catagory'
            no_of_seats = request.POST.get('no_of_seats')
 
            # Fetch seat price from database
            try:
                seat_obj = SeatType.objects.get(event_id=event_id, seat_name=seat_catagory)
                seat_price = seat_obj.seat_price
            except SeatType.DoesNotExist:
                messages.error(request, f"Seat category '{seat_catagory}' not found for this event.")
                return redirect('booking_details_view')
           
            total_amount = (int(no_of_seats) * int(seat_price))
            # print("-----",total_amount)        
           
            print ("--->>>>>",event_id,email_id,seat_catagory,no_of_seats,seat_price,total_amount)
            if not all([name, email_id, B_date, phone_number, event_id]):
                messages.error(request, "All fields are required")
                return redirect('booking_events')
 
            event_obj = events.objects.get(event_id=event_id)
 
            booking = BookingEvents.objects.create(
                name=name,
                email_id=email_id,
                B_date=datetime.strptime(B_date, "%Y-%m-%d").date(),
                phone_number=phone_number,
                seat_catagory=seat_catagory,
                no_of_seats=int(no_of_seats),
                total_amount=int(total_amount),
                Event=event_obj,
                payment_status='pending'
            )
 
            # Stripe Checkout Session
            stripe.api_key = settings.STRIPE_TEST_SECRET_KEY
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'inr',
                        'product_data': {
                            'name': f"{event_obj.title} - {seat_catagory}",
                        },
                        'unit_amount': int(total_amount) * 100,  # convert to subunits (cents/paise)
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.build_absolute_uri('/success/') + f"?session_id={{CHECKOUT_SESSION_ID}}&booking_id={booking.id}",
                cancel_url=request.build_absolute_uri('/cancel/'),
            )
 
            return redirect(checkout_session.url, code=303)
 
        except Exception as e:
            print("BOOKING ERROR:", e)
            messages.error(request, "Booking failed")
        return redirect('Live_Events')
 
def create_checkout_session(request):
    if request.method == 'POST':
        try:
            stripe.api_key = settings.STRIPE_TEST_SECRET_KEY
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {'name': 'Test Product'},
                        'unit_amount': 1000,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url='http://localhost:8000/success/?session_id={CHECKOUT_SESSION_ID}',
                cancel_url='http://localhost:8000/cancel',
            )
            # Track the payment session
            Payment.objects.create(
                stripe_session_id=session.id,
                amount=1000,
                status='pending'
            )
            return JsonResponse({'id': session.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=403)
    return JsonResponse({'error': 'Invalid request'}, status=400)
 
def payment_success(request):
    session_id = request.GET.get('session_id')
    booking_id = request.GET.get('booking_id')
    movie_booking_id = request.GET.get('movie_booking_id')
    context = {}
   
    if booking_id:
        try:
            from .models import BookingEvents
            booking = BookingEvents.objects.get(id=booking_id)
            booking.payment_status = 'completed'
            booking.save()
            context['booking'] = booking
            context['event'] = booking.Event
            messages.success(request, f"Payment successful for {booking.Event.title}!")
        except BookingEvents.DoesNotExist:
            pass
 
    if movie_booking_id:
        try:
            from .models import booking_details
            mb = booking_details.objects.get(id=movie_booking_id)
            mb.payment_status = 'completed'
            mb.save()
            context['movie_booking'] = mb
            context['movie'] = mb.movie_id
           
            # Generate PDF Ticket
            ticket_id = str(uuid.uuid4())[:8]
            folder = os.path.join(settings.MEDIA_ROOT, "tickets")
            os.makedirs(folder, exist_ok=True)
            file_path = os.path.join(folder, f"ticket_{ticket_id}.pdf")
            pdf = canvas.Canvas(file_path)
            pdf.setFont("Helvetica-Bold", 20)
            pdf.drawString(200, 800, "MOVIE TICKET")
            pdf.setFont("Helvetica", 12)
            y = 750
            details = [
                f"Ticket ID: {ticket_id}",
                f"Movie: {mb.movie_id.name}",
                f"Cinema: {mb.cinema_id.cinema_name}",
                f"Name: {mb.name}",
                f"Email: {mb.email_id}",
                f"Phone: {mb.phone_number}",
                f"Category: {mb.seat_category}",
                f"Seats: {mb.no_of_tickets}",
                f"Total: ₹{mb.total_amount}",
            ]
            for item in details:
                pdf.drawString(100, y, item)
                y -= 30
            pdf.save()
            context['ticket_url'] = f"/media/tickets/ticket_{ticket_id}.pdf"
            messages.success(request, f"Payment successful for {mb.movie_id.name}!")
        except Exception as e:
            print("MOVIE SUCCESS ERROR:", e)
 
    if session_id:
        try:
            from .models import Payment
            payment, created = Payment.objects.get_or_create(stripe_session_id=session_id, defaults={'amount': 0})
            payment.status = 'completed'
            if booking_id:
                from .models import BookingEvents
                booking = BookingEvents.objects.get(id=booking_id)
                payment.amount = booking.total_amount * 100
                payment.email = booking.email_id
            elif movie_booking_id:
                from .models import booking_details
                mb = booking_details.objects.get(id=movie_booking_id)
                payment.amount = mb.total_amount * 100
                payment.email = mb.email_id
            payment.save()
            context['payment'] = payment
        except:
            pass
           
    return render(request, 'booking_conformed.html', context)
 
def payment_cancel(request):
    return HttpResponse("Payment Cancelled")
 
 
def Live_Events(request):
    events_all = events.objects.all()
    return render(request, 'Live_Events.html', {'events': events_all})

def show_event_by_id(request, id):
    request.session['id'] = id
    request.session['event_id'] = id
    event_one = events.objects.get(event_id=id)
    # bring the seattype from the database where the id is matched and having seatprice of seatprice is the lowest

    seat_price=SeatType.objects.filter(event_id=id).aggregate(Min('seat_price'))['seat_price__min']
    return render(request, 'show_event_by_id.html', {'event': event_one, 'seatprice': seat_price})

def delete_event(request, id):
    event_one = events.objects.get(id=id)
    event_one.delete()
    return HttpResponse(f"Event Deleted: {event_one.title}")


def get_events(request):
    events_all = events.objects.all()
    return render(request, 'get_events.html', {'events': events_all})

def send_otp(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        event_id = request.POST.get('event_id')
        request.session['event_id'] = event_id
        otp_val = random.randint(1000, 9999)
        request.session['otp'] = otp_val
        request.session['email'] = email
        
        # Save to Database for admin viewing
        otp.objects.create(otp=otp_val)
        
        print("\n\n" + "="*50)
        print(f"YOUR OTP IS: {otp_val}")
        print("="*50 + "\n\n")
        
        # Email Logic
        try:
            msg = MIMEMultipart()
            msg['From'] = 'xpertinfotech.inq@gmail.com'
            msg['To'] = email
            msg['Subject'] = 'OTP for login'
            body = f'Your OTP is {otp_val}'
            msg.attach(MIMEText(body, 'plain'))
            
            #Uncomment below to actually send
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(msg['From'], 'icwznxetbonwouvn')
            server.send_message(msg)
            server.quit()
        except:
            pass 

        return JsonResponse({'success': True, 'message': 'OTP sent successfully'})
    else:
        return render(request, 'send_otp.html')

def match_otp(request):
    if request.method == 'POST':
        otp = request.session.get('otp')
        user_otp = request.POST.get('otp')
        
        if str(user_otp) == str(otp):
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'message': 'OTP does not match'})
    elif request.method == 'GET':
        return render(request, 'match_otp.html')

def booking_details_view(request):
    myid = request.session.get('event_id') or request.session.get('id')
    email = request.session.get('email')
    
    if not myid:
        return redirect('Live_Events')
        
    event_one = get_object_or_404(events, event_id=myid)
    # Get all seat types for this event with full object data
    seat_types = SeatType.objects.filter(event_id=myid).order_by('seat_price')
    
    if not seat_types.exists():
        messages.error(request, "No seat categories available for this event. Please contact support.")
        return redirect('Live_Events')
    
    return render(request, 'booking_details.html', {
        'event': event_one, 
        'seat_types': seat_types,
        'emailid': email
    })


def booking_conformed(request, id=None):
    context = {}
    if id:
        request.session['id'] = id
        try:
            event_one = events.objects.get(event_id=id)
            context['event'] = event_one
        except events.DoesNotExist:
            pass
    return render(request, 'booking_conformed.html', context)




 
def history_view(request):
    email = request.session.get('email')
    bookings = None
 
    if request.method == "POST":
        email_input = request.POST.get('email')
        if BookingEvents.objects.filter(email_id=email_input).exists():
            # email match found
            request.session['email'] = email_input
            bookings = BookingEvents.objects.filter(email_id=email_input)
            # Pass flag to show JS alert
            return render(request, 'history.html', {
                'bookings': bookings,
                'match_found': True
            })
        else:
            messages.error(request, "No booking found with this email.")
 
    elif email:
        # If session exists
        bookings =  BookingEvents.objects.filter(email_id=email)
 
    return render(request, 'history.html', {
        'bookings': bookings
    })

def history_logout(request):
    if 'email' in request.session:
        del request.session['email']  # remove session
    return redirect('history')
 
def addevents(request):
    if request.method == "POST":
        try:
            event = events.objects.create(
                title=request.POST.get("title"), 
                venue=request.POST.get("venue"), 
                category=request.POST.get("category"),
                languages=request.POST.get("languages"),
                description=request.POST.get("description"),
                event_date=request.POST.get("event_date"),
                event_time=request.POST.get("event_time"),
                duration=request.POST.get("duration"),
                AgeLimit=request.POST.get("AgeLimit"),
                image=request.FILES.get("image"),
                artist_name=request.POST.get("artist_name"),
                artist_picture=request.FILES.get("artist_picture"),
            )

            seat_count = request.POST.get("seat_count")

            if seat_count:
                seat_count = int(seat_count)

                for i in range(1, seat_count + 1):
                    SeatType.objects.create(
                        event=event,
                        seat_name=request.POST.get(f"seat_name_{i}"),
                        seat_price=request.POST.get(f"seat_price_{i}"),
                        seat_total=request.POST.get(f"seat_total_{i}"), # Use seat_total field from model
                    )

            messages.success(request, "Event added successfully!")
            return redirect("Live_Events")
        except Exception as e:
            print(f"Error adding event: {e}")
            messages.error(request, f"Error adding event: {e}")
            return redirect("addevents")

    return render(request, "add_events_by_user.html")


#movies views
def show_movies(request):
    # Fetch all movies from the database
    print("Inside show_movies view")
    moviesall = movie.objects.all()
    print("Movies fetched:", moviesall)
    return render(request, "Live_Movies.html", {"movies": moviesall})   

def delete_movie(request, id):
    movie_one = movie.objects.get(id=id)
    movie_one.delete()
    return HttpResponse(f"Movie Deleted: {movie_one.name}")

def update_movie(request, id):
    movie_one = movie.objects.get(id=id)
    movie_one.title = request.POST.get('title')
    movie_one.price = request.POST.get('price')
    movie_one.save()
    return HttpResponse(f"Movie Updated: {movie_one.name}")

def add_movies(request):
    if request.method == 'POST':
        movie_name = request.POST.get('movie_name')
        price = request.POST.get('price')
        movie_obj = movie.objects.create(
            name=movie_name,
            price=price,
            description=request.POST.get('description'),
            time=request.POST.get('time'),      
        )
        return HttpResponse(f"Movie Added: {movie_name}")
    
def delete_movie_by_id(request, id):
    movie_one = movie.objects.get(id=id)
    movie_one.delete()
    return HttpResponse(f"Movie Deleted: {movie_one.name}")

def get_movies(request):
    movies_all = movie.objects.all()
    return render(request, 'get_movies.html', {'movies': movies_all})

def update_movie_by_id(request, id):
    movie_one = movie.objects.get(id=id)
    movie_one.name = request.POST.get('title')
    movie_one.description = request.POST.get('price')
    movie_one.release_date = request.POST.get('description')
    movie_one.genre = request.POST.get('time')
    
    movie_one.save()
    return HttpResponse(f"Movie Updated: {movie_one.name}")

def movie_booking(request, id):
    movie_obj = movie.objects.get(id=id)
   
    # get cinema_id which is foreign key in cinema model has movie_id as foreign key
    cinema_list = cinemas.objects.filter(movie_id=movie_obj.id)
    context = {
        'movie': movie_obj,
        'cinema': cinema_list,
    }
    print("Cinema fetched:", cinema_list)
    request.session['cinema_id'] = cinema_list.first().cinema_id
    # request.session['show_time'] = cinema_list.show_time
    request.session['screen_no'] = cinema_list.first().screen_no
    for c in cinema_list:
        print("Cinema:", c)
    return render(request, 'movie_booking.html', {'movie': movie_obj, 'cinemas': cinema_list})

def show_movie_by_id(request, movie_id, cinema_id):
    movie_obj = get_object_or_404(movie, id=movie_id) 
    cinema_obj = get_object_or_404(cinemas, id=cinema_id)

    context = {
        'movie': movie_obj,
        'cinema': cinema_obj,
    }
    return render(request, 'show_movie_by_id.html', context)

def seat_selection(request, cinema_id, movie_id):
    cinema_obj = cinemas.objects.get(cinema_id=cinema_id)
    movie_obj = movie.objects.get(id=movie_id)

    seat_layout_data = seat_layout.objects.first()  # Gold / Silver / Platinum

    booked_seats = booking_details.objects.filter(
        cinema_id=cinema_obj,
        movie_id=movie_obj
    ).values_list('no_of_tickets', flat=True)

    context = {
        'movie': movie_obj,
        'cinema': cinema_obj,
        'seat_layout_movie': seat_layout_data,
        'booked_seats': sum(booked_seats)
    }


    return render(request, 'seat_selection.html', context)


def generate_ticket(request):

    if request.method == "POST":

        # session values
        cinema_id1 = request.session.get('cinema_id')
        movie_id_session = request.session.get('movie_id')
        show_time = request.session.get('show_time')
        release_date = request.session.get('release_date')
        director = request.session.get('director')
        cast = request.session.get('cast')

        # form values
        movie_id_post = request.POST.get('movie_id')
        name = request.POST.get("name")
        email = request.POST.get("email_id")
        phone = request.POST.get("phone_number")
        b_date = request.POST.get("birth_date")

        seat_category = request.POST.get("seat_category")
        price = request.POST.get("price_per_ticket")
        seats = request.POST.get("no_of_tickets")
        screen = request.POST.get("screen_no")

        # CRITICAL VALIDATION: Ensure movie_id hasn't been tampered with
        if not movie_id_session or not movie_id_post:
            return HttpResponse("Error: Movie selection is missing. Please start booking again.")
        
        if str(movie_id_session) != str(movie_id_post):
            return HttpResponse("Error: Movie selection mismatch. You cannot change the movie mid-booking. Please start over.")

        if not b_date:
            return HttpResponse("Birth date required")

        birth_date = datetime.strptime(b_date, "%Y-%m-%d").date()

        # calculate total
        total_amount = int(seats) * int(price)

        try:
            cinema_id_obj = cinemas.objects.get(cinema_id=cinema_id1)
            movie_obj = movie.objects.get(id=movie_id_session)
        except (cinemas.DoesNotExist, movie.DoesNotExist):
            return HttpResponse("Error: Invalid cinema or movie selection")

        # create booking object
        obj = booking_details()
        obj.name = name
        obj.email_id = email
        obj.phone_number = phone
        obj.birth_date = birth_date
        obj.seat_category = seat_category
        obj.no_of_tickets = seats
        obj.price_per_ticket = price
        obj.screen_no = screen
        obj.total_amount = total_amount
        obj.cinema_id = cinema_id_obj
        obj.movie_id = movie_obj
        obj.show_time = show_time
        obj.release_date = release_date
        obj.director = director
        obj.cast = cast
        obj.save()

        # Redirect to payment page instead of generating ticket
        request.session['booking_id'] = obj.id
        return redirect(f'/amount-pay/?booking_id={obj.id}')

    return HttpResponse("Invalid request")

def booking_page(request):
    email = request.session.get('email')
    bookings = None

    if request.method == "POST":
        email_input = request.POST.get('email')
        if booking_details.objects.filter(email_id=email_input).exists():
            # email match found
            request.session['email'] = email_input
            bookings = booking_details.objects.filter(email_id=email_input)
            # Pass flag to show JS alert
            return render(request, 'booking_page.html', {
                'bookings': bookings,
                'match_found': True
            })
        else:
            messages.error(request, "No booking found with this email.")

    elif email:
        # If session exists
        bookings = booking_details.objects.filter(email_id=email)

    return render(request, 'booking_page.html', {
        'bookings': bookings
    })

def booking_logout(request):
    if 'email' in request.session:
        del request.session['email']  
    return redirect('booking_page')


# Stripe Payment Views
def create_checkout_session(request):
    """Create a Stripe checkout session or process COD payment"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            booking_id = data.get('booking_id')
            total_amount = data.get('total_amount')
            payment_mode = data.get('payment_mode', 'card')
            
            # Retrieve booking details
            booking = booking_details.objects.get(id=booking_id)
            
            if payment_mode == 'cod':
                # Process Cash on Delivery
                request.session['payment_mode'] = 'cod'
                return JsonResponse({'success': True, 'message': 'COD booking confirmed'})
            
            elif payment_mode == 'card':
                # Process Card payment via Stripe
                # Convert amount to cents (Stripe expects amount in smallest currency unit)
                amount_cents = int(float(total_amount) * 100)
                
                # Create Stripe checkout session
                session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=[{
                        'price_data': {
                            'currency': 'inr',
                            'product_data': {
                                'name': f'Movie Ticket - {booking.movie_id.name}',
                                'description': f'Booking ID: {booking_id}',
                            },
                            'unit_amount': amount_cents,
                        },
                        'quantity': 1,
                    }],
                    mode='payment',
                    success_url=request.build_absolute_uri('/booking-success/') + f'?booking_id={booking_id}',
                    cancel_url=request.build_absolute_uri('/amount-pay/'),
                    metadata={
                        'booking_id': booking_id,
                        'email': booking.email_id,
                    }
                )
                
                request.session['payment_mode'] = 'card'
                return JsonResponse({'sessionId': session.id})
            
            else:
                return JsonResponse({'error': 'Invalid payment mode'}, status=400)
            
        except booking_details.DoesNotExist:
            return JsonResponse({'error': 'Booking not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)


def booking_success(request):
    """Handle successful payment"""
    booking_id = request.GET.get('booking_id')
    
    if booking_id:
        try:
            booking = booking_details.objects.get(id=booking_id)
            # Update booking status to 'Confirmed' if there's a status field
            # booking.status = 'Confirmed'
            # booking.save()
            
            context = {
                'booking': booking,
                'receipt_number': f"REC{int(booking_id):06d}",
            }
            return render(request, 'booking_conformed.html', context)
        except booking_details.DoesNotExist:
            messages.error(request, "Booking not found")
            return redirect('show_movies')
    
    return redirect('show_movies')


def amount_pay(request):
    """Display payment page for a booking"""
    booking_id = request.GET.get('booking_id') or request.session.get('booking_id')
    
    if not booking_id:
        messages.error(request, "No booking selected for payment")
        return redirect('show_movies')
    
    try:
        booking = booking_details.objects.get(id=booking_id)
        context = {
            'booking': booking,
            'stripe_public_key': settings.STRIPE_TEST_PUBLIC_KEY,
            'amount': booking.total_amount,
        }
        return render(request, 'Amount_pay.html', context)
    except booking_details.DoesNotExist:
        messages.error(request, "Booking not found")
        return redirect('show_movies')
    

def send_otp_movie(request):

    print("inside send otp movie function")

    # GET data from movie page
    cinema_id = request.GET.get('cinema_id')
    movie_id = request.GET.get('movie_id')
    show_time = request.GET.get('show_time')
    screen_no = request.GET.get('screen_no')
    release_date = request.GET.get('release_date')
    director = request.GET.get('director')
    cast = request.GET.get('cast')

    print("GET DATA:", cinema_id, movie_id, show_time, screen_no, release_date, director, cast)

    if request.method == 'POST':

        cinema_id = request.POST.get('cinema_id')
        movie_id = request.POST.get('movie_id')
        show_time = request.POST.get('show_time')
        screen_no = request.POST.get('screen_no')
        step = request.POST.get('step')
        
       

        print(f"POST DATA - Cinema: {cinema_id}, Movie: {movie_id}, Time: {show_time}, Screen: {screen_no}, Step: {step}, Release: {release_date}, Director: {director}, Cast: {cast}")

        request.session['cinema_id'] = cinema_id
        request.session['movie_id'] = movie_id
        request.session['show_time'] = show_time
        request.session['screen_no'] = screen_no
       

        if step == 'send':

            email = request.POST.get('email')

            otp = random.randint(1000,9999)
            request.session['otp'] = str(otp)

            print("Generated OTP:", otp)

            msg = MIMEMultipart()
            msg['From'] = 'xpertinfotech.inq@gmail.com'
            msg['To'] = email
            msg['Subject'] = 'OTP for Booking'

            msg.attach(MIMEText(f'Your OTP is {otp}','plain'))

            # server = smtplib.SMTP('smtp.gmail.com',587)
            # server.starttls()
            # server.login(msg['From'],'icwznxetbonwouvn')
            # server.sendmail(msg['From'],email,msg.as_string())
            # server.quit()

            return render(request,'match_otp_movie.html')


        if step == 'verify':

            entered_otp = request.POST.get('otp')
            session_otp = request.session.get('otp')

            print("Entered OTP:", entered_otp)
            print("Session OTP:", session_otp)

            if entered_otp == session_otp:

                cinema_id = request.session.get('cinema_id')
                movie_id = request.session.get('movie_id')
                show_time = request.session.get('show_time')
                screen_no = request.session.get('screen_no')
              

                print("Booking Data:",cinema_id, movie_id, show_time, screen_no)

                return render(request,'booking.html',{
                    'cinema_id':cinema_id,
                    'movie_id':movie_id,
                    'show_time':show_time,
                    'screen_no':screen_no,
                    'release_date': release_date,
                    'director': director,
                    'cast': cast
                })

            else:

                return render(request,'match_otp_movie.html',{
                    'error':'Invalid OTP'
                })

    return render(request,'send_otp_movie.html',{
        'cinema_id':cinema_id,
        'movie_id':movie_id,
        'show_time':show_time,
        'screen_no':screen_no,
        'release_date': release_date,
        'director': director,
        'cast': cast
    })

def match_otp_movie(request):
    if request.method == 'POST':
        otp = request.session.get('otp')   
        user_otp = request.POST.get('otp')

        if str(user_otp) == str(otp):
            print("matching otp")
            cinema_id = request.session.get('cinema_id')
            movie_id = request.session.get('movie_id')
            show_time = request.session.get('show_time')
            screen_no = request.session.get('screen_no')
            release_date = request.session.get('release_date')
            director = request.session.get('director')
            cast = request.session.get('cast')  
            print (cinema_id, movie_id, show_time, screen_no, release_date, director, cast)
            return render(request, 'booking.html',{'cinema_id':cinema_id, 'movie_id':movie_id, 'show_time':show_time,'screen_no':screen_no,'release_date':release_date,'director':director,'cast':cast})
        else:
            return HttpResponse("OTP does not match")

    elif request.method == 'GET':
        return render(request, 'match_otp_movie.html') 