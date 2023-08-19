import random
import string

from django.contrib.auth.models import AbstractUser
from django.db import models


# ----------------------------------------------------------------------------------------------------------------------
# Create models
class User(AbstractUser):
    username = None
    password = models.CharField(max_length=256)
    phone_number = models.CharField(unique=True, max_length=12)
    invite_code = models.CharField(unique=True, max_length=6)
    invited_by_code = models.CharField(max_length=6, null=True)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    @staticmethod
    def generate_one_time_password() -> str:
        """
        Generate random password with 4 digits
        Returns:
             string with password
        """
        return str(random.randint(1000, 9999))

    def generate_invite_code(self) -> None:
        """
        Generate random code using letters and digits and save it in user instance
        Returns:
             None
        """
        chars: str = string.ascii_letters + string.digits
        self.invite_code = ''.join(random.choice(chars) for _ in range(6))
        self.save()
