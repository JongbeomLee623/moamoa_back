from django.contrib import admin
from rest_framework_simplejwt.token_blacklist.admin import OutstandingTokenAdmin
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from .models import User

class CustomOutstandingTokenAdmin(OutstandingTokenAdmin):
    def has_delete_permission(self, *args, **kwargs):
        return True

admin.site.unregister(OutstandingToken)
admin.site.register(User)

# 커스텀 어드민 클래스로 등록
admin.site.register(OutstandingToken, CustomOutstandingTokenAdmin)

