<script setup lang="ts">
import { computed } from "vue";
import type { Song } from "../types/models";

export interface TrackRow {
  key: string;
  mode: "existing" | "new";
  songId: number | null;
  newSongTitle: string;
  trackNumber: number | null;
}

const props = defineProps<{
  rows: TrackRow[];
  songs: Song[];
}>();

const emit = defineEmits<{
  "update:rows": [TrackRow[]];
}>();

function makeKey(): string {
  return Math.random().toString(36).slice(2);
}

function addRow() {
  emit("update:rows", [
    ...props.rows,
    { key: makeKey(), mode: "existing", songId: null, newSongTitle: "", trackNumber: null },
  ]);
}

function removeRow(key: string) {
  emit(
    "update:rows",
    props.rows.filter((row) => row.key !== key)
  );
}

function patchRow(key: string, patch: Partial<TrackRow>) {
  emit(
    "update:rows",
    props.rows.map((row) => (row.key === key ? { ...row, ...patch } : row))
  );
}

/** track_number values that appear more than once among the current rows. */
const duplicateTrackNumbers = computed(() => {
  const counts = new Map<number, number>();
  for (const row of props.rows) {
    if (row.trackNumber === null) continue;
    counts.set(row.trackNumber, (counts.get(row.trackNumber) ?? 0) + 1);
  }
  const duplicates = new Set<number>();
  for (const [number, count] of counts) {
    if (count > 1) duplicates.add(number);
  }
  return duplicates;
});

function rowError(row: TrackRow): string | null {
  if (row.trackNumber !== null && duplicateTrackNumbers.value.has(row.trackNumber)) {
    return `Номер трека ${row.trackNumber} повторяется.`;
  }
  if (row.mode === "existing" && row.songId === null) {
    return "Выберите песню.";
  }
  if (row.mode === "new" && row.newSongTitle.trim() === "") {
    return "Введите название новой песни.";
  }
  if (row.trackNumber === null || row.trackNumber < 1) {
    return "Укажите номер трека (>= 1).";
  }
  return null;
}

const hasErrors = computed(() => props.rows.some((row) => rowError(row) !== null));

defineExpose({ hasErrors });
</script>

<template>
  <div class="space-y-3">
    <div
      v-for="row in rows"
      :key="row.key"
      class="flex flex-wrap items-start gap-2 rounded border border-gray-200 p-3"
    >
      <select
        :value="row.mode"
        class="rounded border border-gray-300 px-2 py-1 text-sm"
        @change="
          patchRow(row.key, {
            mode: ($event.target as HTMLSelectElement).value as 'existing' | 'new',
          })
        "
      >
        <option value="existing">Существующая песня</option>
        <option value="new">Новая песня</option>
      </select>

      <select
        v-if="row.mode === 'existing'"
        :value="row.songId ?? ''"
        class="min-w-[200px] flex-1 rounded border border-gray-300 px-2 py-1 text-sm"
        @change="
          patchRow(row.key, {
            songId: ($event.target as HTMLSelectElement).value
              ? Number(($event.target as HTMLSelectElement).value)
              : null,
          })
        "
      >
        <option value="" disabled>Выберите песню…</option>
        <option v-for="song in songs" :key="song.id" :value="song.id">{{ song.title }}</option>
      </select>

      <input
        v-else
        type="text"
        placeholder="Название новой песни"
        :value="row.newSongTitle"
        class="min-w-[200px] flex-1 rounded border border-gray-300 px-2 py-1 text-sm"
        @input="patchRow(row.key, { newSongTitle: ($event.target as HTMLInputElement).value })"
      />

      <input
        type="number"
        min="1"
        placeholder="№ трека"
        :value="row.trackNumber ?? ''"
        class="w-24 rounded border border-gray-300 px-2 py-1 text-sm"
        @input="
          patchRow(row.key, {
            trackNumber: ($event.target as HTMLInputElement).value
              ? Number(($event.target as HTMLInputElement).value)
              : null,
          })
        "
      />

      <button
        type="button"
        class="rounded px-2 py-1 text-sm text-red-600 hover:bg-red-50"
        @click="removeRow(row.key)"
      >
        Удалить
      </button>

      <p v-if="rowError(row)" class="w-full text-sm text-red-600">{{ rowError(row) }}</p>
    </div>

    <button
      type="button"
      class="rounded border border-gray-300 px-3 py-1.5 text-sm hover:bg-gray-50"
      @click="addRow"
    >
      + Добавить трек
    </button>
  </div>
</template>
