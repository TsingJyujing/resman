from django.contrib import admin

# Register your models here.

from .models import (
    ImageThread,
    DefaultS3Image,
    ReactionImageThread,
    HttpImage
)
admin.site.register(ImageThread)
admin.site.register(ReactionImageThread)
admin.site.register(DefaultS3Image)
admin.site.register(HttpImage)
