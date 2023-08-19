import re

from django.contrib.auth import get_user_model
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field, extend_schema_serializer, OpenApiExample
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.request import Request

# ----------------------------------------------------------------------------------------------------------------------
# Get user model
User = get_user_model()


# ----------------------------------------------------------------------------------------------------------------------
# Create serializers
@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name='phone number example',
            value={'phone_number': '+79991234567'},
            request_only=True,
        ),
    ]
)
class UserIdentificationSerializer(serializers.ModelSerializer):
    """
    Serializer for the user identification/registration
    """
    phone_number = serializers.CharField(max_length=12)

    class Meta:
        model = User
        fields = [
            'phone_number',
        ]

    def validate_phone_number(self, phone_number: str) -> str:
        """
        Check field using regular expressions
        Args:
            phone_number: string number from user
        Returns:
            checked string or raise exception
        """
        if not re.match(r'^[+][7][\d]{10}$', phone_number):
            raise serializers.ValidationError('Incorrect phone number')

        return phone_number


# ------------------------------------------------------------------------------
@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name='password example',
            value={'password': '0000'},
            request_only=True,
        ),
    ]
)
class UserAuthenticationSerializer(serializers.ModelSerializer):
    """
    Serializer for the user authentication with one time password
    """
    password = serializers.CharField(max_length=4)

    class Meta:
        model = User
        fields = [
            'password',
        ]

    def validate_password(self, password: str) -> str:
        """
        Check field using regular expressions
        Args:
            password: string password from user
        Returns:
            checked string or raise exception
        """
        if not len(password) == 4:
            raise serializers.ValidationError('Password must have only 4 digits')
        elif not re.match(r'^\d{4}$', password):
            raise serializers.ValidationError('Password must have digits only')

        return password


# ------------------------------------------------------------------------------
class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the user profile
    """
    invited_users = SerializerMethodField()
    invited_by_code = serializers.CharField(required=True, max_length=6)

    class Meta:
        model = User
        fields = [
            'id',
            'phone_number',
            'invite_code',
            'invited_by_code',
            'invited_users'
        ]
        read_only_fields = ['phone_number', 'invite_code']

    def update(self, user: User, validated_data: dict) -> User:
        """
        Update invited_by_code field with given code from user
        Args:
            user: user instance to update
            validated_data: validated data dict from request
        Returns:
            updated user instance
        """
        user.invited_by_code = validated_data['invited_by_code']
        user.save(update_fields=('invited_by_code',))

        return user

    def validate_invited_by_code(self, invited_by_code: str) -> str:
        """
        Check field using regular expressions
        Args:
            invited_by_code: string code from user
        Returns:
            checked string or raise exception
        """
        request: Request = self.context['request']

        if not re.match(r'^[a-zA-Z0-9]{6}$', invited_by_code):
            raise serializers.ValidationError('Incorrect code')

        elif request.user.invited_by_code:
            raise serializers.ValidationError('Invitation code has already been used')

        elif not User.objects.filter(
                invite_code=request.data['invited_by_code']
        ).exists() or request.data['invited_by_code'] == request.user.invite_code:
            raise serializers.ValidationError('Invalid invitation code')

        return invited_by_code

    @extend_schema_field(OpenApiTypes.ANY)
    def get_invited_users(self, user: User) -> list | list[str]:
        """
        Get list of invited phone numbers
        Args:
            user: user instance
        Returns:
            empty list or list with phone numbers
        """
        return [user.phone_number for user in User.objects.filter(invited_by_code=user.invite_code)]
