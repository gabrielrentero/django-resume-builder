from django.contrib import admin

from . import models


@admin.register(models.Resume)
class Resume(admin.ModelAdmin):
    list_display = ('title',)


@admin.register(models.ResumeItem)
class ResumeItemAdmin(admin.ModelAdmin):
    list_display = ('resume', 'title', 'company', 'start_date')
    ordering = ('resume', '-start_date')
