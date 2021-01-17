from django.contrib import admin

# Register your models here.

from .models import (
    ImageList,
    VideoList,
    Novel,
    S3Image,
    S3Video,
)

admin.site.register(VideoList)
admin.site.register(Novel)
admin.site.register(ImageList)
admin.site.register(S3Image)
admin.site.register(S3Video)
