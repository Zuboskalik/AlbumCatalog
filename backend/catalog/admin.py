from django.contrib import admin

from .models import Album, AlbumSong, Artist, Song


class AlbumSongInline(admin.TabularInline):
    model = AlbumSong
    extra = 1
    autocomplete_fields = ["song"]
    ordering = ["track_number"]


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ["title", "artist", "release_year"]
    list_filter = ["artist"]
    search_fields = ["title", "artist__name"]
    autocomplete_fields = ["artist"]
    inlines = [AlbumSongInline]


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ["title"]
    search_fields = ["title"]


@admin.register(AlbumSong)
class AlbumSongAdmin(admin.ModelAdmin):
    list_display = ["album", "track_number", "song"]
    list_filter = ["album"]
    autocomplete_fields = ["album", "song"]
