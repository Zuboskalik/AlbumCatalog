from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    AlbumTrackDetailView,
    AlbumTrackListCreateView,
    AlbumViewSet,
    ArtistViewSet,
    SongViewSet,
)

router = DefaultRouter()
router.register("artists", ArtistViewSet, basename="artist")
router.register("albums", AlbumViewSet, basename="album")
router.register("songs", SongViewSet, basename="song")

urlpatterns = [
    path(
        "albums/<int:album_pk>/tracks/",
        AlbumTrackListCreateView.as_view(),
        name="album-track-list",
    ),
    path(
        "albums/<int:album_pk>/tracks/<int:pk>/",
        AlbumTrackDetailView.as_view(),
        name="album-track-detail",
    ),
] + router.urls
