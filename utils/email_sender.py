from flask_mail import Message
from extensions import mail
from flask import current_app

def send_booking_email(to_email, booking_data, pdf_buffer):
    """
    Sends a booking confirmation email with the ticket PDF attached.
    """
    try:
        subject = f"Booking Confirmation: {booking_data.get('museum_name')}"
        
        msg = Message(subject, recipients=[to_email])
        
        msg.body = f"""
        Hello {booking_data.get('user_name', 'Visitor')},

        Thank you for booking with PixelPast!

        Your booking details:
        Museum: {booking_data.get('museum_name')}
        Date: {booking_data.get('date')}
        Tickets: {booking_data.get('tickets')}
        Booking ID: {booking_data.get('booking_id')}

        Your official ticket is attached to this email. Please show it at the entrance.

        Enjoy your visit!
        
        Best regards,
        The PixelPast Team
        """
        
        # Attach PDF
        msg.attach(
            filename="Museum_Ticket.pdf",
            content_type="application/pdf",
            data=pdf_buffer.getvalue()
        )
        
        mail.send(msg)
        print(f"Email sent to {to_email}")
        return True
    
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
