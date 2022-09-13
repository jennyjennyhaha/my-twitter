from django.contrib import admin
from tweets.models import Tweet


# admin means staff and he can see all the tweets and their posters.
# for data operation
# Register your models here.
@admin.register(Tweet)
class TweetAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = (
        'created_at',
        'user',
        'content',
    )
