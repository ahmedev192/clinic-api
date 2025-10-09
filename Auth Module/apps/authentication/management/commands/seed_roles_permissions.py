"""
Management command to seed roles and permissions.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.authorization.models import Role, Permission, Resource, Action
from apps.oauth2.models import OAuth2Provider

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed roles and permissions for the authentication system'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--business-type',
            type=str,
            choices=['lms', 'hms', 'marketplace', 'generic'],
            default='generic',
            help='Business type to seed data for'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding'
        )
    
    def handle(self, *args, **options):
        business_type = options['business_type']
        clear = options['clear']
        
        if clear:
            self.stdout.write('Clearing existing data...')
            self.clear_data()
        
        self.stdout.write(f'Seeding data for {business_type} business type...')
        
        # Seed resources and actions
        self.seed_resources_and_actions()
        
        # Seed permissions
        self.seed_permissions(business_type)
        
        # Seed roles
        self.seed_roles(business_type)
        
        # Seed OAuth2 providers
        self.seed_oauth_providers()
        
        self.stdout.write(
            self.style.SUCCESS('Successfully seeded roles and permissions!')
        )
    
    def clear_data(self):
        """Clear existing data."""
        Role.objects.all().delete()
        Permission.objects.all().delete()
        Resource.objects.all().delete()
        Action.objects.all().delete()
        OAuth2Provider.objects.all().delete()
    
    def seed_resources_and_actions(self):
        """Seed basic resources and actions."""
        self.stdout.write('Seeding resources and actions...')
        
        # Resources
        resources = [
            ('user', 'User', 'User management', 'model'),
            ('role', 'Role', 'Role management', 'model'),
            ('permission', 'Permission', 'Permission management', 'model'),
            ('audit', 'Audit Log', 'Audit log management', 'model'),
            ('oauth2', 'OAuth2 Provider', 'OAuth2 provider management', 'model'),
            ('profile', 'User Profile', 'User profile management', 'model'),
            ('session', 'User Session', 'User session management', 'model'),
        ]
        
        for name, display_name, description, resource_type in resources:
            Resource.objects.get_or_create(
                name=name,
                defaults={
                    'display_name': display_name,
                    'description': description,
                    'resource_type': resource_type,
                    'is_active': True
                }
            )
        
        # Actions
        actions = [
            ('create', 'Create', 'Create new records'),
            ('read', 'Read', 'View records'),
            ('update', 'Update', 'Modify records'),
            ('delete', 'Delete', 'Remove records'),
            ('list', 'List', 'List records'),
            ('export', 'Export', 'Export data'),
            ('import', 'Import', 'Import data'),
        ]
        
        for name, display_name, description in actions:
            Action.objects.get_or_create(
                name=name,
                defaults={
                    'display_name': display_name,
                    'description': description,
                    'is_active': True
                }
            )
    
    def seed_permissions(self, business_type):
        """Seed permissions based on business type."""
        self.stdout.write('Seeding permissions...')
        
        # Base permissions for all business types
        base_permissions = [
            ('user.create', 'Create User', 'Create new users', 'user', 'create'),
            ('user.read', 'Read User', 'View user information', 'user', 'read'),
            ('user.update', 'Update User', 'Modify user information', 'user', 'update'),
            ('user.delete', 'Delete User', 'Remove users', 'user', 'delete'),
            ('user.list', 'List Users', 'List all users', 'user', 'list'),
            ('role.create', 'Create Role', 'Create new roles', 'role', 'create'),
            ('role.read', 'Read Role', 'View role information', 'role', 'read'),
            ('role.update', 'Update Role', 'Modify role information', 'role', 'update'),
            ('role.delete', 'Delete Role', 'Remove roles', 'role', 'delete'),
            ('role.list', 'List Roles', 'List all roles', 'role', 'list'),
            ('permission.create', 'Create Permission', 'Create new permissions', 'permission', 'create'),
            ('permission.read', 'Read Permission', 'View permission information', 'permission', 'read'),
            ('permission.update', 'Update Permission', 'Modify permission information', 'permission', 'update'),
            ('permission.delete', 'Delete Permission', 'Remove permissions', 'permission', 'delete'),
            ('permission.list', 'List Permissions', 'List all permissions', 'permission', 'list'),
            ('audit.read', 'Read Audit Log', 'View audit logs', 'audit', 'read'),
            ('audit.list', 'List Audit Logs', 'List all audit logs', 'audit', 'list'),
            ('oauth2.create', 'Create OAuth2 Provider', 'Create new OAuth2 providers', 'oauth2', 'create'),
            ('oauth2.read', 'Read OAuth2 Provider', 'View OAuth2 provider information', 'oauth2', 'read'),
            ('oauth2.update', 'Update OAuth2 Provider', 'Modify OAuth2 provider information', 'oauth2', 'update'),
            ('oauth2.delete', 'Delete OAuth2 Provider', 'Remove OAuth2 providers', 'oauth2', 'delete'),
            ('oauth2.list', 'List OAuth2 Providers', 'List all OAuth2 providers', 'oauth2', 'list'),
        ]
        
        # Business-specific permissions
        business_permissions = {
            'lms': [
                ('course.create', 'Create Course', 'Create new courses', 'course', 'create'),
                ('course.read', 'Read Course', 'View course information', 'course', 'read'),
                ('course.update', 'Update Course', 'Modify course information', 'course', 'update'),
                ('course.delete', 'Delete Course', 'Remove courses', 'course', 'delete'),
                ('course.list', 'List Courses', 'List all courses', 'course', 'list'),
                ('enrollment.create', 'Create Enrollment', 'Create new enrollments', 'enrollment', 'create'),
                ('enrollment.read', 'Read Enrollment', 'View enrollment information', 'enrollment', 'read'),
                ('enrollment.update', 'Update Enrollment', 'Modify enrollment information', 'enrollment', 'update'),
                ('enrollment.delete', 'Delete Enrollment', 'Remove enrollments', 'enrollment', 'delete'),
                ('enrollment.list', 'List Enrollments', 'List all enrollments', 'enrollment', 'list'),
                ('assignment.create', 'Create Assignment', 'Create new assignments', 'assignment', 'create'),
                ('assignment.read', 'Read Assignment', 'View assignment information', 'assignment', 'read'),
                ('assignment.update', 'Update Assignment', 'Modify assignment information', 'assignment', 'update'),
                ('assignment.delete', 'Delete Assignment', 'Remove assignments', 'assignment', 'delete'),
                ('assignment.list', 'List Assignments', 'List all assignments', 'assignment', 'list'),
            ],
            'hms': [
                ('patient.create', 'Create Patient', 'Create new patients', 'patient', 'create'),
                ('patient.read', 'Read Patient', 'View patient information', 'patient', 'read'),
                ('patient.update', 'Update Patient', 'Modify patient information', 'patient', 'update'),
                ('patient.delete', 'Delete Patient', 'Remove patients', 'patient', 'delete'),
                ('patient.list', 'List Patients', 'List all patients', 'patient', 'list'),
                ('appointment.create', 'Create Appointment', 'Create new appointments', 'appointment', 'create'),
                ('appointment.read', 'Read Appointment', 'View appointment information', 'appointment', 'read'),
                ('appointment.update', 'Update Appointment', 'Modify appointment information', 'appointment', 'update'),
                ('appointment.delete', 'Delete Appointment', 'Remove appointments', 'appointment', 'delete'),
                ('appointment.list', 'List Appointments', 'List all appointments', 'appointment', 'list'),
                ('medical_record.create', 'Create Medical Record', 'Create new medical records', 'medical_record', 'create'),
                ('medical_record.read', 'Read Medical Record', 'View medical record information', 'medical_record', 'read'),
                ('medical_record.update', 'Update Medical Record', 'Modify medical record information', 'medical_record', 'update'),
                ('medical_record.delete', 'Delete Medical Record', 'Remove medical records', 'medical_record', 'delete'),
                ('medical_record.list', 'List Medical Records', 'List all medical records', 'medical_record', 'list'),
            ],
            'marketplace': [
                ('product.create', 'Create Product', 'Create new products', 'product', 'create'),
                ('product.read', 'Read Product', 'View product information', 'product', 'read'),
                ('product.update', 'Update Product', 'Modify product information', 'product', 'update'),
                ('product.delete', 'Delete Product', 'Remove products', 'product', 'delete'),
                ('product.list', 'List Products', 'List all products', 'product', 'list'),
                ('order.create', 'Create Order', 'Create new orders', 'order', 'create'),
                ('order.read', 'Read Order', 'View order information', 'order', 'read'),
                ('order.update', 'Update Order', 'Modify order information', 'order', 'update'),
                ('order.delete', 'Delete Order', 'Remove orders', 'order', 'delete'),
                ('order.list', 'List Orders', 'List all orders', 'order', 'list'),
                ('inventory.create', 'Create Inventory', 'Create new inventory items', 'inventory', 'create'),
                ('inventory.read', 'Read Inventory', 'View inventory information', 'inventory', 'read'),
                ('inventory.update', 'Update Inventory', 'Modify inventory information', 'inventory', 'update'),
                ('inventory.delete', 'Delete Inventory', 'Remove inventory items', 'inventory', 'delete'),
                ('inventory.list', 'List Inventory', 'List all inventory items', 'inventory', 'list'),
            ],
        }
        
        # Create all permissions
        all_permissions = base_permissions + business_permissions.get(business_type, [])
        
        for name, display_name, description, resource, action in all_permissions:
            Permission.objects.get_or_create(
                name=name,
                defaults={
                    'display_name': display_name,
                    'description': description,
                    'resource': resource,
                    'action': action,
                    'is_active': True,
                    'is_system': True
                }
            )
    
    def seed_roles(self, business_type):
        """Seed roles based on business type."""
        self.stdout.write('Seeding roles...')
        
        # Base roles for all business types
        base_roles = [
            ('super_admin', 'Super Administrator', 'Full system access', True),
            ('admin', 'Administrator', 'Administrative access', True),
            ('user', 'User', 'Basic user access', True),
        ]
        
        # Business-specific roles
        business_roles = {
            'lms': [
                ('instructor', 'Instructor', 'Course instructor access', False),
                ('student', 'Student', 'Student access', False),
                ('course_admin', 'Course Administrator', 'Course management access', False),
            ],
            'hms': [
                ('doctor', 'Doctor', 'Doctor access', False),
                ('nurse', 'Nurse', 'Nurse access', False),
                ('receptionist', 'Receptionist', 'Receptionist access', False),
                ('patient', 'Patient', 'Patient access', False),
            ],
            'marketplace': [
                ('seller', 'Seller', 'Product seller access', False),
                ('buyer', 'Buyer', 'Product buyer access', False),
                ('inventory_manager', 'Inventory Manager', 'Inventory management access', False),
                ('order_manager', 'Order Manager', 'Order management access', False),
            ],
        }
        
        # Create all roles
        all_roles = base_roles + business_roles.get(business_type, [])
        
        for name, display_name, description, is_system in all_roles:
            role, created = Role.objects.get_or_create(
                name=name,
                defaults={
                    'display_name': display_name,
                    'description': description,
                    'is_active': True,
                    'is_system': is_system
                }
            )
            
            if created:
                # Assign permissions to roles
                self.assign_permissions_to_role(role, business_type)
    
    def assign_permissions_to_role(self, role, business_type):
        """Assign permissions to a role."""
        # Super admin gets all permissions
        if role.name == 'super_admin':
            permissions = Permission.objects.filter(is_active=True)
            for permission in permissions:
                role.role_permissions.get_or_create(permission=permission)
        
        # Admin gets most permissions except super admin specific ones
        elif role.name == 'admin':
            permissions = Permission.objects.filter(
                is_active=True
            ).exclude(
                name__in=['user.delete', 'role.delete', 'permission.delete', 'oauth2.delete']
            )
            for permission in permissions:
                role.role_permissions.get_or_create(permission=permission)
        
        # User gets basic permissions
        elif role.name == 'user':
            permissions = Permission.objects.filter(
                is_active=True,
                name__in=[
                    'user.read', 'user.update', 'profile.read', 'profile.update'
                ]
            )
            for permission in permissions:
                role.role_permissions.get_or_create(permission=permission)
        
        # Business-specific role permissions
        elif business_type == 'lms':
            if role.name == 'instructor':
                permissions = Permission.objects.filter(
                    is_active=True,
                    name__in=[
                        'course.read', 'course.update', 'assignment.create',
                        'assignment.read', 'assignment.update', 'assignment.delete',
                        'enrollment.read', 'user.read'
                    ]
                )
                for permission in permissions:
                    role.role_permissions.get_or_create(permission=permission)
            
            elif role.name == 'student':
                permissions = Permission.objects.filter(
                    is_active=True,
                    name__in=[
                        'course.read', 'assignment.read', 'enrollment.read',
                        'user.read', 'user.update', 'profile.read', 'profile.update'
                    ]
                )
                for permission in permissions:
                    role.role_permissions.get_or_create(permission=permission)
        
        elif business_type == 'hms':
            if role.name == 'doctor':
                permissions = Permission.objects.filter(
                    is_active=True,
                    name__in=[
                        'patient.read', 'patient.update', 'appointment.read',
                        'appointment.update', 'medical_record.create',
                        'medical_record.read', 'medical_record.update',
                        'user.read'
                    ]
                )
                for permission in permissions:
                    role.role_permissions.get_or_create(permission=permission)
            
            elif role.name == 'nurse':
                permissions = Permission.objects.filter(
                    is_active=True,
                    name__in=[
                        'patient.read', 'appointment.read', 'appointment.update',
                        'medical_record.read', 'user.read'
                    ]
                )
                for permission in permissions:
                    role.role_permissions.get_or_create(permission=permission)
        
        elif business_type == 'marketplace':
            if role.name == 'seller':
                permissions = Permission.objects.filter(
                    is_active=True,
                    name__in=[
                        'product.create', 'product.read', 'product.update',
                        'product.delete', 'order.read', 'inventory.read',
                        'inventory.update', 'user.read'
                    ]
                )
                for permission in permissions:
                    role.role_permissions.get_or_create(permission=permission)
            
            elif role.name == 'buyer':
                permissions = Permission.objects.filter(
                    is_active=True,
                    name__in=[
                        'product.read', 'order.create', 'order.read',
                        'user.read', 'user.update', 'profile.read', 'profile.update'
                    ]
                )
                for permission in permissions:
                    role.role_permissions.get_or_create(permission=permission)
    
    def seed_oauth_providers(self):
        """Seed OAuth2 providers."""
        self.stdout.write('Seeding OAuth2 providers...')
        
        # Google OAuth2 provider
        OAuth2Provider.objects.get_or_create(
            name='google',
            defaults={
                'display_name': 'Google',
                'provider_type': 'google',
                'is_active': True,
                'client_id': 'your-google-client-id',
                'client_secret': 'your-google-client-secret',
                'authorization_url': 'https://accounts.google.com/o/oauth2/v2/auth',
                'token_url': 'https://oauth2.googleapis.com/token',
                'user_info_url': 'https://www.googleapis.com/oauth2/v2/userinfo',
                'jwks_url': 'https://www.googleapis.com/oauth2/v3/certs',
                'scopes': ['openid', 'profile', 'email'],
                'default_scopes': ['openid', 'profile', 'email'],
                'supports_oidc': True,
                'issuer': 'https://accounts.google.com',
                'pkce_required': True,
                'state_required': True,
                'nonce_required': True,
                'redirect_uris': ['http://localhost:8000/api/v1/oauth2/callback/'],
                'claim_mapping': {
                    'sub': 'external_user_id',
                    'email': 'email',
                    'given_name': 'first_name',
                    'family_name': 'last_name',
                    'picture': 'avatar'
                },
                'jit_provisioning': True,
                'auto_assign_roles': ['user'],
                'require_email_verification': False
            }
        )
        
        # Microsoft OAuth2 provider
        OAuth2Provider.objects.get_or_create(
            name='microsoft',
            defaults={
                'display_name': 'Microsoft',
                'provider_type': 'microsoft',
                'is_active': True,
                'client_id': 'your-microsoft-client-id',
                'client_secret': 'your-microsoft-client-secret',
                'authorization_url': 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize',
                'token_url': 'https://login.microsoftonline.com/common/oauth2/v2.0/token',
                'user_info_url': 'https://graph.microsoft.com/v1.0/me',
                'jwks_url': 'https://login.microsoftonline.com/common/discovery/v2.0/keys',
                'scopes': ['openid', 'profile', 'email'],
                'default_scopes': ['openid', 'profile', 'email'],
                'supports_oidc': True,
                'issuer': 'https://login.microsoftonline.com/common/v2.0',
                'pkce_required': True,
                'state_required': True,
                'nonce_required': True,
                'redirect_uris': ['http://localhost:8000/api/v1/oauth2/callback/'],
                'claim_mapping': {
                    'sub': 'external_user_id',
                    'email': 'email',
                    'given_name': 'first_name',
                    'surname': 'last_name'
                },
                'jit_provisioning': True,
                'auto_assign_roles': ['user'],
                'require_email_verification': False
            }
        )
        
        # GitHub OAuth2 provider
        OAuth2Provider.objects.get_or_create(
            name='github',
            defaults={
                'display_name': 'GitHub',
                'provider_type': 'github',
                'is_active': True,
                'client_id': 'your-github-client-id',
                'client_secret': 'your-github-client-secret',
                'authorization_url': 'https://github.com/login/oauth/authorize',
                'token_url': 'https://github.com/login/oauth/access_token',
                'user_info_url': 'https://api.github.com/user',
                'scopes': ['user:email'],
                'default_scopes': ['user:email'],
                'supports_oidc': False,
                'pkce_required': True,
                'state_required': True,
                'nonce_required': False,
                'redirect_uris': ['http://localhost:8000/api/v1/oauth2/callback/'],
                'claim_mapping': {
                    'id': 'external_user_id',
                    'login': 'external_username',
                    'email': 'email',
                    'name': 'full_name'
                },
                'jit_provisioning': True,
                'auto_assign_roles': ['user'],
                'require_email_verification': False
            }
        )

