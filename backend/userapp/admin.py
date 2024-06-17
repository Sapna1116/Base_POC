from django.contrib import admin
from userapp.models import User,Profile

class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email']


class ProfileAdmin(admin.ModelAdmin):
    # To be able to edit the 'verified' checkbox from dashboard only, w/o entering the individual profile
    list_editable = ['verified']
    list_display = ['user', 'full_name' ,'verified']

admin.site.register(User, UserAdmin)
admin.site.register( Profile,ProfileAdmin)