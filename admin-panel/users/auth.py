import http
import logging
import uuid
import jwt
import requests

from django.conf import settings
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.cache import cache

User = get_user_model()
logger = logging.getLogger(__name__)


def request_auth(request_id, username, password):
    url = settings.AUTH_API_LOGIN_URL
    payload = {"login": username, "password": password}
    headers = {"X-Request-Id": request_id}

    try:
        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == http.HTTPStatus.UNAUTHORIZED:
            raise ValueError("Incorrect username or password.")
        elif response.status_code == http.HTTPStatus.INTERNAL_SERVER_ERROR:
            raise ValueError("Auth service unavailable.")
        elif response.status_code != http.HTTPStatus.OK:
            raise ValueError("Internal Service Error.")

        return response.json()

    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending request to auth service: {e}")
        raise


def decode_jwt_token(token):
    try:
        return jwt.decode(token, options={"verify_signature": False}, algorithms=["HS256"])
    except jwt.InvalidTokenError:
        logger.error("Invalid JWT token")
        raise ValueError("Invalid JWT token")


def update_user(decoded_token, username, data):
    try:
        user, created = User.objects.get_or_create(
            id=decoded_token["sub"],
            defaults={
                "username": username,
                "first_name": data.get("first_name"),
                "last_name": data.get("last_name"),
                "is_active": data.get("is_active", True),
                "is_admin": True,
                "is_staff": True,
                "is_superuser": True,
                "last_token_check": timezone.now(),
            },
        )

        if not created:
            user.first_name = data.get("first_name")
            user.last_name = data.get("last_name")
            user.is_active = data.get("is_active", True)
            user.is_admin = True
            user.is_staff = True
            user.is_superuser = True
            user.last_token_check = timezone.now()
            user.save()

        return user

    except Exception as e:
        logger.error(f"Error updating user: {e}")
        raise


class CustomBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        request_id = request.META.get("HTTP_X_REQUEST_ID", str(uuid.uuid4()))
        cache_key = f"user_auth_{username}"
        cached_user = cache.get(cache_key)

        if cached_user:
            logger.debug(f"User {username} found in cache.")
            return cached_user

        try:
            data = request_auth(request_id, username, password)
            jwt_token = data.get("access_token")

            decoded_token = decode_jwt_token(jwt_token)

            if "ADMIN" in decoded_token.get("roles", []):
                user = update_user(decoded_token, username, data)
                cache.set(cache_key, user, timeout=60 * 60)
                logger.debug(f"User {username} authenticated and cached.")
                return user
            else:
                raise ValueError("User does not have required role ADMIN")

        except (ValueError, requests.exceptions.RequestException) as e:
            logger.error(f"Error during authentication: {e}")
            try:
                user = User.objects.get(username=username)
                if user.check_password(password):
                    cache.set(cache_key, user, timeout=60 * 60)
                    logger.debug(f"User {username} found in DB and cached after failed auth service call.")
                    return user
            except User.DoesNotExist:
                logger.warning(f"User {username} does not exist.")
                return None

        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            logger.warning(f"User with id {user_id} not found.")
            return None
