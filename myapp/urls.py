from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='index'),    
    
    # Authentication URLs
    path('login_view/', views.login_view, name='login_view'),
    path('logout/', views.logout_view, name='logout'),
    path('register_view/', views.register_view, name='register_view'),
    
    path('Live_Events/', views.Live_Events, name='Live_Events'),
    path('event', views.event, name='event'),
    path('eventlist', views.eventlist, name='eventlist'),
    path('eventsingle', views.eventsingle, name='eventsingle'),
    path('show_event_by_id/<int:id>', views.show_event_by_id, name='show_event_by_id'),    
    path('get_events', views.get_events, name='get_events'),    
    path('booking_conformed', views.booking_conformed, name='booking_conformed'),
    path('send_otp', views.send_otp, name='send_otp'),
    path('match_otp', views.match_otp, name='match_otp'),
    # URL name stays 'booking_events' (for forms), but view is 'booking_events_view'
    path('booking_events', views.booking_events_view, name='booking_events'),
    path('booking_details_view', views.booking_details_view, name='booking_details_view'),
    path('booking_conformed/<int:id>', views.booking_conformed, name='booking_conformed'),
    path('show_movies/', views.show_movies, name='show_movies'),
    path('addevents', views.addevents, name='addevents'),
    path('history', views.history_view, name='history'),
    path('history_logout', views.history_logout, name='history_logout'),
    path('show_movie_by_id/<int:movie_id>/<int:cinema_id>/', views.show_movie_by_id, name='show_movie_by_id'),
    path('movie_booking/<int:id>/', views.movie_booking, name='movie_booking'),
    path('seat_selection/<int:cinema_id>/<int:movie_id>/', views.seat_selection, name='seat_selection'),
    path('bookings/', views.booking_page, name='booking_page'),
    path('booking_page/', views.booking_page, name='booking_page1'),
    path('booking_logout/', views.booking_logout, name='booking_logout'),
    path('send_otp_movie/', views.send_otp_movie, name='send_otp_movie'),
    path('match_otp_movie/', views.match_otp_movie, name='match_otp_movie'),
    path("generate-ticket/", views.generate_ticket, name="generate_ticket"),
    
    # Stripe Payment URLs
    path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),
    path('amount-pay/', views.amount_pay, name='amount_pay'),
    path('booking-success/', views.booking_success, name='booking_success'),
    path("success/", views.payment_success, name="payment_success"),
    path("cancel/", views.payment_cancel, name="payment_cancel"),
]