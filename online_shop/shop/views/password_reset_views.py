from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from shop.serializers import PasswordResetRequestSerializer, User, SetNewPasswordSerializer


class PasswordResetRequestAPIView(APIView):
    permission_classes = []  # AllowAny

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        user = User.objects.get(email=email)

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        # ბმული API endpoint-ზე
        reset_link = f"http://127.0.0.1:8000/api/password-reset-confirm/{uid}/{token}/"

        send_mail(
            subject="Password Reset Request",
            message=f"Click the link below to reset your password:\n{reset_link}",
            from_email=None,
            recipient_list=[email],
            fail_silently=False,
        )

        return Response({"message": "Password reset link sent."}, status=status.HTTP_200_OK)


class PasswordResetConfirmAPIView(APIView):
    permission_classes = []  # AllowAny

    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"error": "Invalid link"}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, token):
            return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = SetNewPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user.set_password(serializer.validated_data["new_password"])
        user.save()

        return Response({"message": "Password reset successful"}, status=status.HTTP_200_OK)