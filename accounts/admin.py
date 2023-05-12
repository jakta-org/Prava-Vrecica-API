from django.contrib import admin
from .models import User, Token, EntranceKey, Group, UserGroup

# Register your models here.
admin.site.register(User)
admin.site.register(Token)
admin.site.register(EntranceKey)
admin.site.register(Group)
admin.site.register(UserGroup)