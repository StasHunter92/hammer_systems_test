from django.contrib.auth import get_user_model, authenticate, login, logout
from django.forms import Form
from django.http import HttpResponseRedirect, HttpResponse, HttpRequest
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View

from apps.frontend.users.forms import UserSignupLoginForm, UserAuthenticationForm, InviteCodeForm, UserProfileForm
from apps.users.tasks import send_sms

# ----------------------------------------------------------------------------------------------------------------------
# Get user model
User = get_user_model()


# ----------------------------------------------------------------------------------------------------------------------
# Create views
class UserSignupLoginView(View):
    """
    View for the user identification or registration
    """

    @staticmethod
    def get(request: HttpRequest) -> HttpResponse | HttpResponseRedirect:
        """
        Get login page or redirect to the profile page
        Args:
            request: HttpRequest from user
        Returns:
            - HttpResponse 200 with login page if user is anonymous
            - HttpResponseRedirect 302 with profile page if user is already authenticated
        """
        user: User = request.user

        if not user.is_anonymous:
            return redirect(reverse('user-profile'))

        return render(request, 'login_form.html')

    @staticmethod
    def post(request: HttpRequest) -> HttpResponse | HttpResponseRedirect:
        """
        Get data from login form and redirect to the password confirm page
        or render login page again
        Args:
            request: HttpRequest from user
        Returns:
            - HttpResponseRedirect 302 with password confirm page if data is valid
            - HttpResponse 200 with login page if data is not valid
        """
        user_signup_login_form: Form = UserSignupLoginForm(data=request.POST)

        if user_signup_login_form.is_valid():
            phone_number: str = user_signup_login_form.cleaned_data['phone_number']
            request.session['phone_number'] = phone_number

            user: User = User.objects.filter(phone_number=phone_number).first()
            one_time_password: str = User.generate_one_time_password()
            request.session['one_time_password'] = one_time_password

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

            response: HttpResponseRedirect = redirect(reverse('user-authenticate'))

            return response

        return render(
            request,
            'login_form.html',
            {'form': user_signup_login_form}
        )


# ------------------------------------------------------------------------------
class UserAuthenticationView(View):
    """
    View for the user authentication
    """

    @staticmethod
    def get(request: HttpRequest) -> HttpResponse:
        """
        Get password confirm page
        Args:
            request: HttpRequest from user
        Returns:
            - HttpResponse 200 with login page data is not valid
        """
        one_time_password: str = request.session.get('one_time_password')

        return render(
            request,
            'authorize_form.html',
            {'one_time_password': one_time_password}
        )

    @staticmethod
    def post(request: HttpRequest) -> HttpResponseRedirect:
        """
        Get data from password confirm form and redirect to the profile page
        or login page again
        Args:
            request: HttpRequest from user
        Returns:
            - HttpResponseRedirect 302 with profile page if data is valid
            - HttpResponseRedirect 302 with login page if data is not valid
        """
        user_authentication_form = UserAuthenticationForm(data=request.POST)

        if user_authentication_form.is_valid():
            saved_phone_number: str = request.session.get('phone_number')
            password: str = user_authentication_form.cleaned_data['password']

            user: User = authenticate(
                request,
                phone_number=saved_phone_number,
                password=password
            )

            if user:
                login(request, user)

                return redirect(reverse('user-profile'))
            return redirect(reverse('user-identify'))


# ------------------------------------------------------------------------------
class UserRetrieveView(View):
    """
    View for the user profile
    """

    @staticmethod
    def get(request: HttpRequest) -> HttpResponse | HttpResponseRedirect:
        """
        Get profile page or redirect to the login page
        Args:
            request: HttpRequest from user
        Returns:
            - HttpResponse 200 with profile page if user is authorized
            - HttpResponseRedirect 302 with login page if user is anonymous
        """
        user: User = request.user

        if not user.is_anonymous:
            invited_users: list[str] = [
                user.phone_number for user in User.objects.filter(
                    invited_by_code=request.user.invite_code
                )
            ]

            return render(
                request,
                'profile_form.html',
                {'user': user, 'invited_users': invited_users}
            )
        return redirect(reverse('user-identify'))

    @staticmethod
    def post(request):
        user_profile_form = UserProfileForm(data=request.POST)

        if user_profile_form.is_valid():
            user = request.user

            first_name = user_profile_form.cleaned_data['first_name']
            last_name = user_profile_form.cleaned_data['last_name']
            email = user_profile_form.cleaned_data['email']

            user.first_name = first_name
            user.last_name = last_name
            user.email = email

            user.save(
                update_fields=(
                    'first_name',
                    'last_name',
                    'email'
                )
            )
        return redirect(reverse('user-profile'))


# ------------------------------------------------------------------------------
class UserConfirmInviteView(View):
    """
    View for the invite code confirmation
    """

    @staticmethod
    def post(request: HttpRequest) -> HttpResponseRedirect:
        """
        Update user data and reload page or reload page
        Args:
            request: HttpRequest from user
        Returns:
            - HttpResponseRedirect 302 with profile page
        """
        invite_code_form = InviteCodeForm(data=request.POST)

        if invite_code_form.is_valid():
            user: User = request.user
            invite_code: str = invite_code_form.cleaned_data['invited_by_code']

            if User.objects.filter(
                    invite_code=invite_code
            ).exists() and not invite_code == user.invite_code:
                user.invited_by_code = invite_code
                user.save(
                    update_fields=('invited_by_code',)
                )

        return redirect(reverse('user-profile'))


# ------------------------------------------------------------------------------
class UserLogoutView(View):
    """
    View for the profile logout
    """

    @staticmethod
    def post(request: HttpRequest) -> HttpResponseRedirect:
        """
        Logout user from the page and redirect to the login page
        Args:
            request: HttpRequest from user
        Returns:
             HttpResponseRedirect 302 with login page
        """
        logout(request)

        return redirect(reverse('user-identify'))
