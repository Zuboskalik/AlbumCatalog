import apiClient from "./client";
import type { Song, SongDetail } from "../types/models";

export function getSongs(search = ""): Promise<Song[]> {
  return apiClient
    .get<Song[]>("/songs/", { params: search ? { search } : {} })
    .then((res) => res.data);
}

export function getSong(id: number): Promise<SongDetail> {
  return apiClient.get<SongDetail>(`/songs/${id}/`).then((res) => res.data);
}

export function createSong(title: string): Promise<SongDetail> {
  return apiClient.post<SongDetail>("/songs/", { title }).then((res) => res.data);
}

export function updateSong(id: number, title: string): Promise<SongDetail> {
  return apiClient.patch<SongDetail>(`/songs/${id}/`, { title }).then((res) => res.data);
}

export function deleteSong(id: number): Promise<void> {
  return apiClient.delete(`/songs/${id}/`).then(() => undefined);
}
