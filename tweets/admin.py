from tweets.models import Correction
from django.contrib import admin

class CorrectionAdmin(admin.ModelAdmin):
    list_display = ('proper', 'improper')

admin.site.register(Correction, CorrectionAdmin)
