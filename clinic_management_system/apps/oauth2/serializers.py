"""
OAuth2/OIDC serializers.
"""
from rest_framework import serializers
from .models import OAuth2Provider, OAuth2Session, ExternalAccount, OAuth2Token


class OAuth2ProviderSerializer(serializers.ModelSerializer):
    """Serializer for OAuth2 providers."""
    
    class Meta:
        model = OAuth2Provider
        fields = [
            'id', 'name', 'display_name', 'provider_type', 'is_active',
            'supports_oidc', 'jit_provisioning', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class OAuth2ProviderDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for OAuth2 providers (admin only)."""
    
    class Meta:
        model = OAuth2Provider
        fields = [
            'id', 'name', 'display_name', 'provider_type', 'is_active',
            'client_id', 'authorization_url', 'token_url', 'user_info_url',
            'jwks_url', 'discovery_url', 'scopes', 'default_scopes',
            'supports_oidc', 'issuer', 'pkce_required', 'state_required',
            'nonce_required', 'redirect_uris', 'claim_mapping',
            'group_claim', 'role_claim', 'access_token_lifetime',
            'refresh_token_lifetime', 'jit_provisioning', 'auto_assign_roles',
            'require_email_verification', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class OAuth2SessionSerializer(serializers.ModelSerializer):
    """Serializer for OAuth2 sessions."""
    
    class Meta:
        model = OAuth2Session
        fields = [
            'id', 'provider', 'user', 'is_active', 'created_at',
            'last_used', 'expires_at'
        ]
        read_only_fields = ['id', 'created_at', 'last_used']


class ExternalAccountSerializer(serializers.ModelSerializer):
    """Serializer for external accounts."""
    
    provider = OAuth2ProviderSerializer(read_only=True)
    
    class Meta:
        model = ExternalAccount
        fields = [
            'id', 'provider', 'external_user_id', 'external_username',
            'external_email', 'is_active', 'is_verified', 'created_at',
            'last_used'
        ]
        read_only_fields = ['id', 'created_at', 'last_used']


class OAuth2TokenSerializer(serializers.ModelSerializer):
    """Serializer for OAuth2 tokens."""
    
    provider = OAuth2ProviderSerializer(read_only=True)
    
    class Meta:
        model = OAuth2Token
        fields = [
            'id', 'provider', 'token_type', 'scope', 'is_active',
            'created_at', 'expires_at'
        ]
        read_only_fields = ['id', 'created_at']


class OAuth2AuthorizeSerializer(serializers.Serializer):
    """Serializer for OAuth2 authorization request."""
    
    provider_id = serializers.UUIDField()
    redirect_uri = serializers.URLField(required=False)
    state = serializers.CharField(required=False)
    nonce = serializers.CharField(required=False)
    scopes = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    
    def validate_provider_id(self, value):
        """Validate provider exists and is active."""
        try:
            provider = OAuth2Provider.objects.get(id=value, is_active=True)
            return provider
        except OAuth2Provider.DoesNotExist:
            raise serializers.ValidationError('Invalid or inactive provider.')
    
    def validate_redirect_uri(self, value):
        """Validate redirect URI is allowed."""
        if not value:
            return value
        
        provider = self.initial_data.get('provider_id')
        if provider:
            try:
                provider_obj = OAuth2Provider.objects.get(id=provider)
                if value not in provider_obj.redirect_uris:
                    raise serializers.ValidationError('Invalid redirect URI.')
            except OAuth2Provider.DoesNotExist:
                pass
        
        return value


class OAuth2CallbackSerializer(serializers.Serializer):
    """Serializer for OAuth2 callback."""
    
    code = serializers.CharField()
    state = serializers.CharField()
    error = serializers.CharField(required=False)
    error_description = serializers.CharField(required=False)
    
    def validate(self, attrs):
        """Validate callback data."""
        if attrs.get('error'):
            raise serializers.ValidationError(
                f"OAuth2 error: {attrs.get('error_description', attrs['error'])}"
            )
        
        if not attrs.get('code'):
            raise serializers.ValidationError('Authorization code is required.')
        
        if not attrs.get('state'):
            raise serializers.ValidationError('State parameter is required.')
        
        return attrs


class AccountLinkingSerializer(serializers.Serializer):
    """Serializer for account linking."""
    
    provider_id = serializers.UUIDField()
    external_user_id = serializers.CharField()
    external_username = serializers.CharField(required=False)
    external_email = serializers.EmailField(required=False)
    external_claims = serializers.JSONField(default=dict)
    
    def validate_provider_id(self, value):
        """Validate provider exists and is active."""
        try:
            provider = OAuth2Provider.objects.get(id=value, is_active=True)
            return provider
        except OAuth2Provider.DoesNotExist:
            raise serializers.ValidationError('Invalid or inactive provider.')
    
    def validate(self, attrs):
        """Validate account linking data."""
        provider = attrs['provider_id']
        external_user_id = attrs['external_user_id']
        
        # Check if account is already linked
        if ExternalAccount.objects.filter(
            provider=provider,
            external_user_id=external_user_id
        ).exists():
            raise serializers.ValidationError('Account is already linked.')
        
        return attrs


class AccountUnlinkingSerializer(serializers.Serializer):
    """Serializer for account unlinking."""
    
    external_account_id = serializers.UUIDField()
    
    def validate_external_account_id(self, value):
        """Validate external account exists and belongs to user."""
        try:
            account = ExternalAccount.objects.get(id=value)
            return account
        except ExternalAccount.DoesNotExist:
            raise serializers.ValidationError('External account not found.')
    
    def validate(self, attrs):
        """Validate account unlinking."""
        account = attrs['external_account_id']
        user = self.context['request'].user
        
        if account.user != user:
            raise serializers.ValidationError('Cannot unlink account belonging to another user.')
        
        return attrs

