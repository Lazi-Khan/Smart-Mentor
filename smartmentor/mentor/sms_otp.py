
import os
from twilio.rest import Client


def send_sms_otp(phone_number, otp):
    account_sid = os.environ["TWILIO_ACCOUNT_SID"]
    auth_token = os.environ["TWILIO_AUTH_TOKEN"]
    from_number = os.environ["TWILIO_PHONE_NUMBER"]

    client = Client(account_sid, auth_token)

    message = client.messages.create(
        to=phone_number,
        from_=from_number,
        body=f"Your Smart Mentor OTP is {otp}. It expires in 5 minutes."
    )

    return message.sid


if __name__ == "__main__":
    phone_number = "+918668499392"
    otp = "123456"  # Test only; do not use for real login

    try:
        message_sid = send_sms_otp(phone_number, otp)
        print("SMS request sent successfully.")
        print("Message SID:", message_sid)
    except Exception as error:
        print("SMS sending failed:", error)
