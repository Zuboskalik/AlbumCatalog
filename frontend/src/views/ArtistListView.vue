<script setup lang="ts">
import { onMounted, ref } from "vue";
import { RouterLink } from "vue-router";
import { useArtistsStore } from "../stores/artists";
import { getErrorMessage } from "../api/errors";
import StateMessage from "../components/StateMessage.vue";

const store = useArtistsStore();
const newName = ref("");
const createError = ref<string | null>(null);
const creating = ref(false);

onMounted(() => store.fetchAll());

async function handleCreate() {
  if (!newName.value.trim()) return;
  creating.value = true;
  createError.value = null;
  try {
    await store.create(newName.value.trim());
    newName.value = "";
  } catch (error) {
    createError.value = getErrorMessage(error);
  } finally {
    creating.value = false;
  }
}

async function handleDelete(id: number, name: string) {
  if (!window.confirm(`Удалить исполнителя «${name}»? Все его альбомы также будут удалены.`)) {
    return;
  }
  await store.remove(id);
}
</script>

<template>
  <div class="mx-auto max-w-3xl p-6">
    <h1 class="mb-4 text-2xl font-semibold">Исполнители</h1>

    <form class="mb-6 flex gap-2" @submit.prevent="handleCreate">
      <input
        v-model="newName"
        type="text"
        placeholder="Имя исполнителя"
        class="flex-1 rounded border border-gray-300 px-3 py-2"
      />
      <button
        type="submit"
        :disabled="creating || !newName.trim()"
        class="rounded bg-gray-900 px-4 py-2 text-white disabled:opacity-50"
      >
        Добавить
      </button>
    </form>
    <p v-if="createError" class="-mt-4 mb-4 text-sm text-red-600">{{ createError }}</p>

    <StateMessage
      :loading="store.loading"
      :error="store.error"
      :empty="store.items.length === 0"
      empty-text="Исполнителей пока нет — добавьте первого выше."
    />

    <ul v-if="!store.loading && !store.error" class="divide-y divide-gray-200">
      <li v-for="artist in store.items" :key="artist.id" class="flex items-center justify-between py-3">
        <RouterLink :to="`/artists/${artist.id}`" class="hover:underline">
          {{ artist.name }}
          <span class="text-sm text-gray-500">({{ artist.albums_count }} альбомов)</span>
        </RouterLink>
        <button
          type="button"
          class="text-sm text-red-600 hover:underline"
          @click="handleDelete(artist.id, artist.name)"
        >
          Удалить
        </button>
      </li>
    </ul>
  </div>
</template>
