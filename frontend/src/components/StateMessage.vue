<script setup lang="ts">
defineProps<{
  loading: boolean;
  error: string | null;
  empty?: boolean;
  emptyText?: string;
}>();
</script>

<template>
  <p v-if="loading" class="py-6 text-center text-gray-500">Загрузка…</p>
  <p v-else-if="error" class="rounded border border-red-300 bg-red-50 px-4 py-3 text-red-700">
    {{ error }}
  </p>
  <p v-else-if="empty" class="py-6 text-center text-gray-500">
    {{ emptyText ?? "Пока ничего нет." }}
  </p>
</template>
