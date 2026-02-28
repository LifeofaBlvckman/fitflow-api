from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('bio', 'profile_picture', 'height_cm', 'starting_weight_kg', 'fitness_goal', 'followers')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('email', 'first_name', 'last_name', 'bio', 'profile_picture', 'height_cm', 'starting_weight_kg', 'fitness_goal')}),
    )
    readonly_fields = ('followers',)

admin.site.register(User, CustomUserAdmin)
