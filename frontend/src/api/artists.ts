import apiClient from "./client";
import type { Artist, ArtistDetail } from "../types/models";

export function getArtists(): Promise<Artist[]> {
  return apiClient.get<Artist[]>("/artists/").then((res) => res.data);
}

export function getArtist(id: number): Promise<ArtistDetail> {
  return apiClient.get<ArtistDetail>(`/artists/${id}/`).then((res) => res.data);
}

export function createArtist(name: string): Promise<ArtistDetail> {
  return apiClient.post<ArtistDetail>("/artists/", { name }).then((res) => res.data);
}

export function updateArtist(id: number, name: string): Promise<ArtistDetail> {
  return apiClient.patch<ArtistDetail>(`/artists/${id}/`, { name }).then((res) => res.data);
}

export function deleteArtist(id: number): Promise<void> {
  return apiClient.delete(`/artists/${id}/`).then(() => undefined);
}
