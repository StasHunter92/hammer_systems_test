from django.contrib.auth import get_user_model, authenticate, login, logout
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample

from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.api.v1.users.serializers import UserIdentificationSerializer, UserAuthenticationSerializer, UserSerializer
from apps.users.tasks import send_sms

# ----------------------------------------------------------------------------------------------------------------------
# Get user model
User = get_user_model()


# ----------------------------------------------------------------------------------------------------------------------
# Create views
@extend_schema(tags=['Users'])
class UserSignupLoginView(CreateAPIView):
    """
    CreateAPIView for the user identification or registration
    """
    serializer_class = UserIdentificationSerializer

    @extend_schema(
        summary='Identification/registration',
        description='Identify user by phone number or create a new user',
        # responses={status.HTTP_204_NO_CONTENT: None},
        responses={
            status.HTTP_201_CREATED: OpenApiResponse(
                response=201,
                description='SMS send imitation',
                examples=[OpenApiExample(
                    name='OTP example',
                    value={'one_time_password': '0000'},
                    response_only=True,
                )])},
    )
    def post(self, request: Request, *args, **kwargs) -> Response:
        """
        Identify or create a user using phone number
        Args:
            request: HTTP request
        Returns:
            HTTP response 201 with one time password (for debug only)
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number: str = serializer.validated_data['phone_number']
        request.session['phone_number'] = phone_number

        user: User = User.objects.filter(phone_number=phone_number).first()
        one_time_password: str = User.generate_one_time_password()

        if user:
            user.set_password(one_time_password)
            user.save(update_fields=('password',))
        else:
            new_user: User = User.objects.create(
                phone_number=phone_number,
                password=one_time_password
            )
            new_user.set_password(one_time_password)
            new_user.generate_invite_code()
            new_user.save(
                update_fields=(
                    'password', 'invite_code'
                )
            )

        # SMS send imitation
        send_sms(one_time_password)

        # response = Response(status=status.HTTP_204_NO_CONTENT)
        response = Response(status=status.HTTP_201_CREATED,
                            data={'one_time_password': one_time_password})

        return response


# ------------------------------------------------------------------------------
@extend_schema(tags=['Users'])
class UserAuthenticationView(CreateAPIView):
    """
    CreateAPIView for the user authentication
    """
    serializer_class = UserAuthenticationSerializer

    @extend_schema(
        summary='Authentication',
        description='Authenticate user using one time password',
        responses={
            status.HTTP_201_CREATED: None,
            status.HTTP_400_BAD_REQUEST: None
        }
    )
    def post(self, request: Request, *args, **kwargs) -> Response:
        """
        Authenticate a user using password
        Args:
            request: HTTP request
        Returns:
            - HTTP response 201
            - HTTP response 400
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        saved_phone_number: str = request.session.get('phone_number')

        password: str = serializer.validated_data['password']
        user: User = authenticate(
            request,
            phone_number=saved_phone_number,
            password=password
        )

        if user:
            login(request, user)

            return Response(status=status.HTTP_201_CREATED)

        return Response(status=status.HTTP_400_BAD_REQUEST)


# ------------------------------------------------------------------------------
@extend_schema(tags=['Users'])
class UserRetrieveView(RetrieveUpdateDestroyAPIView):
    """
    RetrieveUpdateDestroyAPIView for the user profile
    """
    serializer_class = UserSerializer
    permission_classes: list = [IsAuthenticated]

    def get_object(self) -> User:
        """
        Get the user
        Returns:
            user instance from request
        """
        return self.request.user

    @extend_schema(
        summary='Profile',
        description='Get user profile',
        responses={
            status.HTTP_200_OK: UserSerializer,
            status.HTTP_403_FORBIDDEN: None,
        }
    )
    def get(self, request: Request, *args, **kwargs) -> Response:
        return self.retrieve(request, *args, **kwargs)

    @extend_schema(
        summary='Invite code confirmation',
        description='Confirm invite code given by other user',
        responses={
            status.HTTP_200_OK: UserSerializer,
            status.HTTP_403_FORBIDDEN: None
        }
    )
    def put(self, request: Request, *args, **kwargs) -> Response:
        return self.update(request, *args, **kwargs)

    @extend_schema(exclude=True)
    def patch(self, request: Request, *args, **kwargs) -> Response:
        return self.partial_update(request, *args, **kwargs)

    @extend_schema(
        summary='Logout',
        description='Logout user from application',
        responses={
            status.HTTP_204_NO_CONTENT: None,
            status.HTTP_403_FORBIDDEN: None
        }
    )
    def delete(self, request: Request, *args, **kwargs) -> Response:
        """
        Logout user from application
        Args:
            request: HTTP request
        Returns:
             HTTP response 204
        """
        logout(request)

        return Response(status=status.HTTP_204_NO_CONTENT)
