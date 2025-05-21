# backend/test_creation/accounts/utils.py
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
import traceback

def send_activation_email(request, user):
    try:
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        current_site = get_current_site(request)
        activation_link = f"http://{current_site.domain}/activate/{uid}/{token}"

        print("🔗 Activation link:", activation_link)  # Debug

        subject = "Activate your account"
        message = render_to_string('activation_email.html', {
            'user': user,
            'activation_link': activation_link,
        })

        email = EmailMessage(subject, message, to=[user.email])
        email.content_subtype = "html"
        email.send()

        print(f"📨 Email sent to {user.email}")

    except Exception as e:
        print("❌ Error sending email:")
        traceback.print_exc()
