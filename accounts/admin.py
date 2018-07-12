from django.contrib import admin
from accounts.models import UserProfile
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


class UserAdminInline(admin.StackedInline):
    model = UserProfile


class UserAdmin(BaseUserAdmin):
    inlines = (UserAdminInline, )


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
