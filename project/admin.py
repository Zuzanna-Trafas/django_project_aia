from django.contrib import admin

from .models import Tournament, SponsorImage, Applicant, Game


class urlInline(admin.TabularInline):
    model = SponsorImage.tournament.through


class TournamentAdmin(admin.ModelAdmin):
    inlines = [
        urlInline,
    ]


class SponsorImageAdmin(admin.ModelAdmin):
    inlines = [
        urlInline,
    ]
    exclude = ('tournament',)


class ApplicantInline(admin.TabularInline):
    model = Applicant.tournament.through


class ApplicantAdmin(admin.ModelAdmin):
    inlines = [
        ApplicantInline,
    ]
    exclude = ('tournament',)


admin.site.register(SponsorImage, SponsorImageAdmin)
admin.site.register(Tournament, TournamentAdmin)
admin.site.register(Applicant, ApplicantAdmin)
admin.site.register(Game)
