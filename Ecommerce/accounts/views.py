from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login,logout
from django.core.mail import send_mail
from django.conf import settings
from .models import CustomUser
from .forms import RegistrationForm, LoginForm
from django.contrib import messages
import random
import string
from django.contrib.auth.decorators import login_required


def index(request):
    return render(request, "index.html")

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            if CustomUser.objects.filter(email=email).exists():
                # Check if the message has already been set
                if not any(message.message == 'Email is already registered' for message in messages.get_messages(request)):
                    messages.error(request, 'Email is already registered')
                return render(request, 'accounts/registration.html', {'form': form})

            otp = generate_otp()
            request.session['otp'] = otp  # Store OTP in session
            request.session['email'] = email  # Store email in session
            request.session['password'] = password  # Store password in session
            send_mail(
                'OTP Verification',
                f'Your OTP is {otp}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )

            return redirect('verify-otp')
    else:
        form = RegistrationForm()
    return render(request, 'accounts/registration.html', {'form': form})


def verify_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        expected_otp = request.session.get('otp')

        if entered_otp == expected_otp:
            email = request.session.get('email')
            password = request.session.get('password')
            username = email.split('@')[0]
            user = CustomUser.objects.create_user(email=email, password=password, username=username)
            del request.session['otp']  # Delete OTP from session
            messages.success(request, 'Email verified successfully. You can now login.')
            return redirect('login_user')
        else:
            # OTP verification failed
            messages.error(request, 'Invalid OTP. Please try again.')
    return render(request, 'accounts/verify_otp.html')


def login_user(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                if user.is_staff:
                    return redirect('admin_main')
                else:
                    return redirect('index')
            else:
                return render(request, 'accounts/login.html', {'form': form, 'error': 'Invalid email or password'})
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('index')

def admin_main(request):
    return render(request,"accounts/admin_main.html")



from django.views import View
from .forms import RegistrationForm, LoginForm, PasswordResetRequestForm, VerifyOTPForm, SetNewPasswordForm


class PasswordResetRequestView(View):
    def get(self, request):
        form = PasswordResetRequestForm()
        return render(request, 'accounts/password_reset_request.html', {'form': form})

    def post(self, request):
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = CustomUser.objects.filter(email=email).first()
            if user:
                otp = generate_otp()
                request.session['otp'] = otp
                request.session['email'] = email

                send_mail(
                    'Password Reset OTP',
                    f'Your OTP is {otp}',
                    settings.EMAIL_HOST_USER,
                    [email],
                    fail_silently=False,
                )

                return redirect('verify_reset_otp')
            else:
                messages.error(request, 'Invalid email address')

        return render(request, 'accounts/password_reset_request.html', {'form': form})

class VerifyResetOTPView(View):
    def get(self, request):
        form = VerifyOTPForm()
        return render(request, 'accounts/verify_otp.html', {'form': form})

    def post(self, request):
        form = VerifyOTPForm(request.POST)
        if form.is_valid():
            entered_otp = form.cleaned_data['otp']
            expected_otp = request.session.get('otp')

            if entered_otp == expected_otp:
                return redirect('set_new_password')
            else:
                messages.error(request, 'Invalid OTP. Please try again.')

        return render(request, 'accounts/verify_otp.html', {'form': form})

class SetNewPasswordView(View):
    def get(self, request):
        form = SetNewPasswordForm()
        return render(request, 'accounts/set_new_password.html', {'form': form})

    def post(self, request):
        form = SetNewPasswordForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            email = request.session.get('email')
            user = CustomUser.objects.filter(email=email).first()
            if user:
                user.set_password(password)
                user.save()
                del request.session['otp']
                del request.session['email']
                messages.success(request, 'Password reset successfully. You can now login.')
                return redirect('login_user')
            else:
                messages.error(request, 'User not found.')

        return render(request, 'accounts/set_new_password.html', {'form': form})












