"""
Custom password validators.
"""
import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class CustomPasswordValidator:
    """
    Custom password validator with additional security requirements.
    """
    
    def __init__(self, min_length=8, require_uppercase=True, require_lowercase=True, 
                 require_digits=True, require_special_chars=True, 
                 max_consecutive_chars=3, common_passwords_file=None):
        self.min_length = min_length
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_digits = require_digits
        self.require_special_chars = require_special_chars
        self.max_consecutive_chars = max_consecutive_chars
        self.common_passwords_file = common_passwords_file
    
    def validate(self, password, user=None):
        """Validate the password."""
        errors = []
        
        # Check minimum length
        if len(password) < self.min_length:
            errors.append(ValidationError(
                _("This password is too short. It must contain at least %(min_length)d characters."),
                code='password_too_short',
                params={'min_length': self.min_length},
            ))
        
        # Check for uppercase letters
        if self.require_uppercase and not re.search(r'[A-Z]', password):
            errors.append(ValidationError(
                _("This password must contain at least one uppercase letter."),
                code='password_no_upper',
            ))
        
        # Check for lowercase letters
        if self.require_lowercase and not re.search(r'[a-z]', password):
            errors.append(ValidationError(
                _("This password must contain at least one lowercase letter."),
                code='password_no_lower',
            ))
        
        # Check for digits
        if self.require_digits and not re.search(r'\d', password):
            errors.append(ValidationError(
                _("This password must contain at least one digit."),
                code='password_no_digit',
            ))
        
        # Check for special characters
        if self.require_special_chars and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append(ValidationError(
                _("This password must contain at least one special character."),
                code='password_no_special',
            ))
        
        # Check for consecutive characters
        if self._has_consecutive_chars(password, self.max_consecutive_chars):
            errors.append(ValidationError(
                _("This password contains too many consecutive characters."),
                code='password_consecutive_chars',
            ))
        
        # Check against common passwords
        if self._is_common_password(password):
            errors.append(ValidationError(
                _("This password is too common."),
                code='password_common',
            ))
        
        # Check against user information
        if user and self._contains_user_info(password, user):
            errors.append(ValidationError(
                _("This password contains user information."),
                code='password_user_info',
            ))
        
        if errors:
            raise ValidationError(errors)
    
    def get_help_text(self):
        """Return help text for the validator."""
        help_texts = []
        
        if self.min_length:
            help_texts.append(f"At least {self.min_length} characters")
        
        if self.require_uppercase:
            help_texts.append("One uppercase letter")
        
        if self.require_lowercase:
            help_texts.append("One lowercase letter")
        
        if self.require_digits:
            help_texts.append("One digit")
        
        if self.require_special_chars:
            help_texts.append("One special character")
        
        if self.max_consecutive_chars:
            help_texts.append(f"Maximum {self.max_consecutive_chars} consecutive characters")
        
        return "Password must contain: " + ", ".join(help_texts)
    
    def _has_consecutive_chars(self, password, max_consecutive):
        """Check if password has too many consecutive characters."""
        if max_consecutive <= 0:
            return False
        
        consecutive_count = 1
        for i in range(1, len(password)):
            if password[i] == password[i-1]:
                consecutive_count += 1
                if consecutive_count > max_consecutive:
                    return True
            else:
                consecutive_count = 1
        
        return False
    
    def _is_common_password(self, password):
        """Check if password is in common passwords list."""
        # This is a simplified check. In production, you might want to use
        # a more comprehensive list or external service.
        common_passwords = {
            'password', '123456', '123456789', 'qwerty', 'abc123',
            'password123', 'admin', 'letmein', 'welcome', 'monkey',
            '1234567890', 'password1', 'qwerty123', 'dragon', 'master'
        }
        
        return password.lower() in common_passwords
    
    def _contains_user_info(self, password, user):
        """Check if password contains user information."""
        user_info = [
            user.username,
            user.email.split('@')[0] if user.email else '',
            user.first_name,
            user.last_name,
        ]
        
        password_lower = password.lower()
        for info in user_info:
            if info and len(info) > 2 and info.lower() in password_lower:
                return True
        
        return False

