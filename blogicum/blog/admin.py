from django.contrib import admin
from blog.models import Post, Category, Location


admin.site.register(Post)
admin.site.register(Category)
admin.site.register(Location)
