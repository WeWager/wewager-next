from fcm_django.models import FCMDevice
from django.contrib.auth.models import User


def send_message_to_user(user: User, title: str, body: str):
    devices = FCMDevice.objects.filter(user=user)
    devices.send_message(title=title, body=body)
