<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { useAlbumsStore } from "../stores/albums";
import { useArtistsStore } from "../stores/artists";
import { useSongsStore } from "../stores/songs";
import { getErrorMessage } from "../api/errors";
import TrackListEditor, { type TrackRow } from "../components/TrackListEditor.vue";
import type { AlbumCreateInput, TrackInput } from "../types/models";

const router = useRouter();
const albumsStore = useAlbumsStore();
const artistsStore = useArtistsStore();
const songsStore = useSongsStore();

const title = ref("");
const artistId = ref<number | "">("");
const releaseYear = ref<number | "">(new Date().getFullYear());
const rows = ref<TrackRow[]>([]);
const trackEditor = ref<InstanceType<typeof TrackListEditor> | null>(null);

const submitting = ref(false);
const submitError = ref<string | null>(null);

onMounted(() => {
  artistsStore.fetchAll();
  songsStore.fetchAll();
});

function toTrackInput(row: TrackRow): TrackInput {
  return row.mode === "existing"
    ? { song_id: row.songId as number, track_number: row.trackNumber as number }
    : { new_song_title: row.newSongTitle.trim(), track_number: row.trackNumber as number };
}

const formValid = () =>
  title.value.trim() !== "" &&
  artistId.value !== "" &&
  releaseYear.value !== "" &&
  !(trackEditor.value?.hasErrors ?? false);

async function handleSubmit() {
  submitError.value = null;
  if (!formValid()) {
    submitError.value = "Заполните все обязательные поля и исправьте ошибки в треклисте.";
    return;
  }

  const payload: AlbumCreateInput = {
    title: title.value.trim(),
    artist_id: artistId.value as number,
    release_year: releaseYear.value as number,
    tracks: rows.value.map(toTrackInput),
  };

  submitting.value = true;
  try {
    const created = await albumsStore.create(payload);
    router.push(`/albums/${created.id}`);
  } catch (error) {
    submitError.value = getErrorMessage(error);
  } finally {
    submitting.value = false;
  }
}
</script>

<template>
  <div class="mx-auto max-w-3xl p-6">
    <h1 class="mb-4 text-2xl font-semibold">Новый альбом</h1>

    <form class="space-y-4" @submit.prevent="handleSubmit">
      <div>
        <label class="mb-1 block text-sm font-medium">Название альбома</label>
        <input v-model="title" type="text" class="w-full rounded border border-gray-300 px-3 py-2" />
      </div>

      <div>
        <label class="mb-1 block text-sm font-medium">Исполнитель</label>
        <select v-model="artistId" class="w-full rounded border border-gray-300 px-3 py-2">
          <option value="" disabled>Выберите исполнителя…</option>
          <option v-for="artist in artistsStore.items" :key="artist.id" :value="artist.id">
            {{ artist.name }}
          </option>
        </select>
      </div>

      <div>
        <label class="mb-1 block text-sm font-medium">Год выпуска</label>
        <input
          v-model.number="releaseYear"
          type="number"
          class="w-full rounded border border-gray-300 px-3 py-2"
        />
      </div>

      <div>
        <label class="mb-1 block text-sm font-medium">Треклист</label>
        <TrackListEditor ref="trackEditor" :rows="rows" :songs="songsStore.items" @update:rows="rows = $event" />
      </div>

      <p v-if="submitError" class="text-sm text-red-600">{{ submitError }}</p>

      <button
        type="submit"
        :disabled="submitting"
        class="rounded bg-gray-900 px-4 py-2 text-white disabled:opacity-50"
      >
        {{ submitting ? "Создание…" : "Создать альбом" }}
      </button>
    </form>
  </div>
</template>
