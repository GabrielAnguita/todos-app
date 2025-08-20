from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.core.exceptions import PermissionDenied
import logging

logger = logging.getLogger(__name__)


class GoogleOnlyAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        # No local signup at all
        return False

    def respond_user_inactive(self, request, user):
        # Block inactive users
        raise PermissionDenied("Account inactive.")


class GoogleOnlySocialAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(self, request, sociallogin):
        # Only allow Google as a provider
        return sociallogin.account.provider == "google"

    def populate_user(self, request, sociallogin, data):
        """
        Trust Google email only if it's marked verified.
        Also ensure username = email for our custom User model.
        """
        logger.debug(f"GoogleOnlySocialAdapter.populate_user called with data: {data}")
        
        user = super().populate_user(request, sociallogin, data)
        
        # Set username = email for our custom User model
        if user.email and not user.username:
            user.username = user.email
            logger.debug(f"Set username to {user.username}")

        # Check if Google email is verified
        email_verified = False
        extra = (sociallogin.account.extra_data or {})
        email_verified = bool(extra.get("email_verified", True))  # Default to True for Google

        if not email_verified:
            logger.error(f"Google email not verified for {user.email}")
            raise PermissionDenied("Google email must be verified.")

        logger.debug(f"User populated successfully: {user.email}")
        return user

    def authentication_error(self, request, provider_id, error=None, exception=None, extra_context=None):
        """
        Handle authentication errors and log them
        """
        logger.error(f"OAuth authentication error for provider {provider_id}")
        logger.error(f"Error: {error}")
        logger.error(f"Exception: {exception}")
        if exception:
            import traceback
            logger.error(f"Exception traceback: {traceback.format_exc()}")
        return super().authentication_error(request, provider_id, error, exception, extra_context)