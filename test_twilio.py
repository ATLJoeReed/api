from twilio.rest import TwilioRestClient

from config import settings


ACCOUNT_SID = settings.TWILIO_ACCOUNT_SID
AUTH_TOKEN = settings.TWILIO_AUTH_TOKEN

client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)

message = client.messages.create(
    to=settings.TWILIO_TO_NUMBER,
    from_=settings.TWILIO_FROM_NUMBER,
    body="Hello there!"
)
