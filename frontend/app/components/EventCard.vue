<template>
  <NuxtLink :to="eventUrl" class="block">
    <UCard class="event-card">
      <!-- Top Image -->
      <img v-if="eventImg" :src="eventImg" :alt="eventName" class="w-full h-48 object-cover rounded-t-md mb-4">
      <div v-else class="w-full h-48 bg-gray-200 rounded-t-md mb-4 flex items-center justify-center">
        <UIcon name="i-lucide-image" class="w-10 h-10 text-gray-400" />
      </div>

      <!-- Event Title -->
      <h3 class="text-lg font-semibold mb-2">
        {{ eventName }}
      </h3>

      <!-- Event Details -->
      <div class="text-sm text-gray-500 mb-3">
        <div class="flex items-center gap-1 mb-1">
          <UIcon name="i-lucide-calendar" class="w-4 h-4" />
          <span>{{ eventDate }}</span>
        </div>
        <div class="flex items-center gap-1 mb-1">
          <UIcon name="i-lucide-tag" class="w-4 h-4" />
          <span>{{ eventType }}</span>
        </div>
        <div class="flex items-center gap-1">
          <UIcon name="i-lucide-map-pin" class="w-4 h-4" />
          <span>{{ eventLocation }}</span>
        </div>
      </div>

      <!-- Event Description (if provided) -->
      <p v-if="eventDescription" class="text-gray-700 mb-4 line-clamp-3">{{ eventDescription }}</p>
    </UCard>
  </NuxtLink>
</template>

<style scoped>
.event-card {
  width: 100%;
  transition: transform 0.2s, box-shadow 0.2s;
}

.event-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}
</style>

<script setup>
defineProps({
  eventName: {
    type: String,
    default: 'Event Name'
  },
  eventDate: {
    type: String,
    default: 'Event Date'
  },
  eventLocation: {
    type: String,
    default: 'Event Location'
  },
  eventImg: {
    type: String,
    default: ''
  },
  eventUrl: {
    type: String,
    default: '#'
  },
  eventType: {
    type: String,
    default: 'Event Type'
  },
  eventDescription: {
    type: String,
    default: ''
  }
});
</script>
