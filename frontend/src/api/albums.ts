import apiClient from "./client";
import type {
  Album,
  AlbumCreateInput,
  AlbumDetail,
  AlbumUpdateInput,
  Track,
  TrackInput,
} from "../types/models";

export function getAlbums(): Promise<Album[]> {
  // The AlbumViewSet has no server-side artist filter (see docs/02_PLAN.md section 3.2),
  // so filtering by artist happens client-side in AlbumListView/the albums store.
  return apiClient.get<Album[]>("/albums/").then((res) => res.data);
}

export function getAlbum(id: number): Promise<AlbumDetail> {
  return apiClient.get<AlbumDetail>(`/albums/${id}/`).then((res) => res.data);
}

export function createAlbum(payload: AlbumCreateInput): Promise<AlbumDetail> {
  return apiClient.post<AlbumDetail>("/albums/", payload).then((res) => res.data);
}

export function updateAlbum(id: number, payload: AlbumUpdateInput): Promise<AlbumDetail> {
  return apiClient.patch<AlbumDetail>(`/albums/${id}/`, payload).then((res) => res.data);
}

export function deleteAlbum(id: number): Promise<void> {
  return apiClient.delete(`/albums/${id}/`).then(() => undefined);
}

export function addTrack(albumId: number, payload: TrackInput): Promise<Track> {
  return apiClient
    .post<Track>(`/albums/${albumId}/tracks/`, payload)
    .then((res) => res.data);
}

export function updateTrack(
  albumId: number,
  trackId: number,
  payload: Partial<TrackInput>
): Promise<Track> {
  return apiClient
    .patch<Track>(`/albums/${albumId}/tracks/${trackId}/`, payload)
    .then((res) => res.data);
}

export function removeTrack(albumId: number, trackId: number): Promise<void> {
  return apiClient.delete(`/albums/${albumId}/tracks/${trackId}/`).then(() => undefined);
}
