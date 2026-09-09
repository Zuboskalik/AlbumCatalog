<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
import { RouterLink, useRoute, useRouter } from "vue-router";
import { useAlbumsStore } from "../stores/albums";
import { useArtistsStore } from "../stores/artists";
import { useSongsStore } from "../stores/songs";
import { getErrorMessage } from "../api/errors";
import StateMessage from "../components/StateMessage.vue";
import type { TrackInput } from "../types/models";

const route = useRoute();
const router = useRouter();
const store = useAlbumsStore();
const artistsStore = useArtistsStore();
const songsStore = useSongsStore();

const newTrackMode = ref<"existing" | "new">("existing");
const newTrackSongId = ref<number | "">("");
const newTrackTitle = ref("");
const newTrackNumber = ref<number | "">("");
const addError = ref<string | null>(null);
const adding = ref(false);

const trackErrors = ref<Record<number, string>>({});

const editing = ref(false);
const editTitle = ref("");
const editArtistId = ref<number | "">("");
const editReleaseYear = ref<number | "">("");
const editError = ref<string | null>(null);
const saving = ref(false);

function load() {
  store.fetchOne(Number(route.params.id));
}

onMounted(() => {
  load();
  artistsStore.fetchAll();
  songsStore.fetchAll();
});
watch(() => route.params.id, load);
watch(
  () => store.current,
  (album) => {
    if (album && !editing.value) {
      editTitle.value = album.title;
      editArtistId.value = album.artist.id;
      editReleaseYear.value = album.release_year;
    }
  },
  { immediate: true }
);

function startEditing() {
  if (!store.current) return;
  editTitle.value = store.current.title;
  editArtistId.value = store.current.artist.id;
  editReleaseYear.value = store.current.release_year;
  editError.value = null;
  editing.value = true;
}

async function handleSaveMetadata() {
  if (!store.current || !editTitle.value.trim() || editArtistId.value === "" || editReleaseYear.value === "") {
    return;
  }
  saving.value = true;
  editError.value = null;
  try {
    await store.update(store.current.id, {
      title: editTitle.value.trim(),
      artist_id: editArtistId.value as number,
      release_year: editReleaseYear.value as number,
    });
    editing.value = false;
  } catch (error) {
    editError.value = getErrorMessage(error);
  } finally {
    saving.value = false;
  }
}

async function handleAddTrack() {
  if (!store.current) return;
  addError.value = null;
  const trackNumber = newTrackNumber.value;
  if (trackNumber === "" || trackNumber < 1) {
    addError.value = "Укажите номер трека (>= 1).";
    return;
  }
  const payload: TrackInput =
    newTrackMode.value === "existing"
      ? { song_id: Number(newTrackSongId.value), track_number: trackNumber }
      : { new_song_title: newTrackTitle.value.trim(), track_number: trackNumber };

  if (newTrackMode.value === "existing" && !newTrackSongId.value) {
    addError.value = "Выберите песню.";
    return;
  }
  if (newTrackMode.value === "new" && !newTrackTitle.value.trim()) {
    addError.value = "Введите название новой песни.";
    return;
  }

  adding.value = true;
  try {
    await store.addTrack(store.current.id, payload);
    newTrackSongId.value = "";
    newTrackTitle.value = "";
    newTrackNumber.value = "";
    await songsStore.fetchAll();
  } catch (error) {
    addError.value = getErrorMessage(error);
  } finally {
    adding.value = false;
  }
}

async function handleTrackNumberChange(trackId: number, value: number) {
  if (!store.current) return;
  trackErrors.value = { ...trackErrors.value, [trackId]: "" };
  try {
    await store.updateTrack(store.current.id, trackId, { track_number: value });
  } catch (error) {
    trackErrors.value = { ...trackErrors.value, [trackId]: getErrorMessage(error) };
  }
}

async function handleRemoveTrack(trackId: number) {
  if (!store.current) return;
  await store.removeTrack(store.current.id, trackId);
}

async function handleDeleteAlbum() {
  if (!store.current) return;
  if (
    !window.confirm(
      `Удалить альбом «${store.current.title}»? Треклист будет удалён, но сами песни останутся в каталоге.`
    )
  ) {
    return;
  }
  await store.remove(store.current.id);
  router.push("/albums");
}
</script>

<template>
  <div class="mx-auto max-w-3xl p-6">
    <RouterLink to="/albums" class="text-sm text-gray-500 hover:underline">&larr; Альбомы</RouterLink>

    <StateMessage :loading="store.loading" :error="store.error" class="mt-4" />

    <div v-if="!store.loading && !store.error && store.current" class="mt-4">
      <div v-if="!editing" class="mb-4 flex items-start justify-between">
        <div>
          <h1 class="text-2xl font-semibold">{{ store.current.title }}</h1>
          <p class="text-gray-500">{{ store.current.artist.name }} · {{ store.current.release_year }}</p>
        </div>
        <div class="flex gap-3">
          <button type="button" class="text-sm text-gray-600 hover:underline" @click="startEditing">
            Изменить
          </button>
          <button type="button" class="text-sm text-red-600 hover:underline" @click="handleDeleteAlbum">
            Удалить альбом
          </button>
        </div>
      </div>

      <form v-else class="mb-6 space-y-3 rounded border border-gray-200 p-4" @submit.prevent="handleSaveMetadata">
        <div>
          <label class="mb-1 block text-sm font-medium">Название альбома</label>
          <input v-model="editTitle" type="text" class="w-full rounded border border-gray-300 px-3 py-2" />
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium">Исполнитель</label>
          <select v-model="editArtistId" class="w-full rounded border border-gray-300 px-3 py-2">
            <option v-for="artist in artistsStore.items" :key="artist.id" :value="artist.id">
              {{ artist.name }}
            </option>
          </select>
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium">Год выпуска</label>
          <input
            v-model.number="editReleaseYear"
            type="number"
            class="w-full rounded border border-gray-300 px-3 py-2"
          />
        </div>
        <p v-if="editError" class="text-sm text-red-600">{{ editError }}</p>
        <div class="flex gap-2">
          <button
            type="submit"
            :disabled="saving"
            class="rounded bg-gray-900 px-4 py-2 text-sm text-white disabled:opacity-50"
          >
            Сохранить
          </button>
          <button
            type="button"
            class="rounded border border-gray-300 px-4 py-2 text-sm"
            @click="editing = false"
          >
            Отмена
          </button>
        </div>
      </form>

      <h2 class="mb-2 text-lg font-medium">Треклист</h2>
      <table v-if="store.current.tracks.length > 0" class="mb-6 w-full border-collapse text-left">
        <thead>
          <tr class="border-b border-gray-300 text-sm text-gray-500">
            <th class="py-2 pr-4">№</th>
            <th class="py-2 pr-4">Песня</th>
            <th class="py-2 pr-4"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="track in store.current.tracks" :key="track.id" class="border-b border-gray-100">
            <td class="py-2 pr-4">
              <input
                type="number"
                min="1"
                :value="track.track_number"
                class="w-20 rounded border border-gray-300 px-2 py-1"
                @change="handleTrackNumberChange(track.id, Number(($event.target as HTMLInputElement).value))"
              />
            </td>
            <td class="py-2 pr-4">
              <RouterLink :to="`/songs/${track.song.id}`" class="hover:underline">
                {{ track.song.title }}
              </RouterLink>
              <p v-if="trackErrors[track.id]" class="text-sm text-red-600">{{ trackErrors[track.id] }}</p>
            </td>
            <td class="py-2 pr-4">
              <button type="button" class="text-sm text-red-600 hover:underline" @click="handleRemoveTrack(track.id)">
                Удалить
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-else class="mb-6 text-gray-500">В этом альбоме пока нет треков.</p>

      <h3 class="mb-2 text-base font-medium">Добавить трек</h3>
      <div class="flex flex-wrap items-start gap-2">
        <select v-model="newTrackMode" class="rounded border border-gray-300 px-2 py-2 text-sm">
          <option value="existing">Существующая песня</option>
          <option value="new">Новая песня</option>
        </select>
        <select
          v-if="newTrackMode === 'existing'"
          v-model="newTrackSongId"
          class="min-w-[200px] flex-1 rounded border border-gray-300 px-2 py-2 text-sm"
        >
          <option value="" disabled>Выберите песню…</option>
          <option v-for="song in songsStore.items" :key="song.id" :value="song.id">{{ song.title }}</option>
        </select>
        <input
          v-else
          v-model="newTrackTitle"
          type="text"
          placeholder="Название новой песни"
          class="min-w-[200px] flex-1 rounded border border-gray-300 px-2 py-2 text-sm"
        />
        <input
          v-model.number="newTrackNumber"
          type="number"
          min="1"
          placeholder="№ трека"
          class="w-24 rounded border border-gray-300 px-2 py-2 text-sm"
        />
        <button
          type="button"
          :disabled="adding"
          class="rounded bg-gray-900 px-3 py-2 text-sm text-white disabled:opacity-50"
          @click="handleAddTrack"
        >
          Добавить
        </button>
      </div>
      <p v-if="addError" class="mt-2 text-sm text-red-600">{{ addError }}</p>
    </div>
  </div>
</template>
