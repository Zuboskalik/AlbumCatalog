from django.shortcuts import get_object_or_404
from rest_framework import generics, viewsets
from rest_framework.filters import SearchFilter

from .models import Album, AlbumSong, Artist, Song
from .serializers import (
    AlbumListSerializer,
    AlbumSerializer,
    AlbumTrackSerializer,
    ArtistListSerializer,
    ArtistSerializer,
    SongListSerializer,
    SongSerializer,
)


class ArtistViewSet(viewsets.ModelViewSet):
    queryset = Artist.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return ArtistListSerializer
        return ArtistSerializer


class SongViewSet(viewsets.ModelViewSet):
    queryset = Song.objects.all()
    filter_backends = [SearchFilter]
    search_fields = ["title"]

    def get_serializer_class(self):
        if self.action == "list":
            return SongListSerializer
        return SongSerializer


class AlbumViewSet(viewsets.ModelViewSet):
    queryset = Album.objects.select_related("artist")

    def get_serializer_class(self):
        if self.action == "list":
            return AlbumListSerializer
        return AlbumSerializer


class AlbumTrackListCreateView(generics.ListCreateAPIView):
    """GET/POST /api/albums/{album_pk}/tracks/ — docs/02_PLAN.md section 3.2."""

    serializer_class = AlbumTrackSerializer

    def get_album(self):
        return get_object_or_404(Album, pk=self.kwargs["album_pk"])

    def get_queryset(self):
        return AlbumSong.objects.filter(album=self.get_album()).select_related("song").order_by(
            "track_number"
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["album"] = self.get_album()
        return context

    def perform_create(self, serializer):
        serializer.save(album=self.get_album())


class AlbumTrackDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PATCH/PUT/DELETE /api/albums/{album_pk}/tracks/{pk}/ — docs/02_PLAN.md section 3.2."""

    serializer_class = AlbumTrackSerializer

    def get_queryset(self):
        return AlbumSong.objects.filter(album_id=self.kwargs["album_pk"]).select_related("song")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["album"] = get_object_or_404(Album, pk=self.kwargs["album_pk"])
        return context
