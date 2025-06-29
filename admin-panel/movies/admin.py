from django import forms
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import (
    FilmWork,
    Genre,
    GenreFilmWork,
    PermissionsEnum,
    Person,
    PersonFilmWork,
)


class FilmWorkForm(forms.ModelForm):
    permissions = forms.MultipleChoiceField(
        choices=PermissionsEnum.choices,
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label=_("Permissions"),
    )

    class Meta:
        model = FilmWork
        fields = "__all__"

    def clean_permissions(self):
        return self.cleaned_data["permissions"]


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    search_fields = ("name",)


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    search_fields = ("full_name",)


class GenreFilmWorkInline(admin.TabularInline):
    model = GenreFilmWork
    autocomplete_fields = ("genre",)


class PersonFilmWorkInline(admin.TabularInline):
    model = PersonFilmWork
    autocomplete_fields = ("person",)


@admin.register(FilmWork)
class FilmWorkAdmin(admin.ModelAdmin):
    form = FilmWorkForm
    inlines = (GenreFilmWorkInline, PersonFilmWorkInline)
    list_display = ("title", "type", "creation_date", "rating", "get_genres", "permissions")
    list_filter = ("type", "genres", "permissions")
    search_fields = ("title", "description", "id")

    def get_queryset(self, request):
        queryset = super().get_queryset(request).prefetch_related("genres")
        return queryset

    def get_genres(self, obj):
        return ",".join([genre.name for genre in obj.genres.all()])

    def get_permissions(self, obj):
        return ", ".join(obj.permissions)

    get_genres.short_description = _("genres")
