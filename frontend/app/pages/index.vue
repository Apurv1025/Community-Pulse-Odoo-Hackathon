<template>
  <UContainer class="py-8">
    <UCard class="w-full max-w-6xl mx-auto">
      <template #header>
        <div class="flex flex-col gap-1">
          <h2 class="text-xl font-semibold">Community Events</h2>
          <p class="text-sm text-gray-500">Discover events happening in your community</p>
        </div>
      </template>

      <div v-if="loading" class="flex justify-center py-8">
        <UButton loading variant="ghost" />
      </div>

      <div v-else-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
        {{ error }}
      </div>

      <div v-else-if="events.length === 0" class="text-center py-10">
        <p class="text-gray-500 text-xl">No events available</p>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-4">
        <EventCard v-for="event in events" :key="event.id" :event-name="event.event_name"
          :event-date="formatDate(event.start_date)" :event-location="`${event.city}, ${event.state}`"
          :event-img="event.img_url" :event-url="`/event/${event.id}`" :event-type="event.category"
          :event-description="event.event_description" />
      </div>
    </UCard>
  </UContainer>
</template>

<script setup>
import { useAuthStore } from "../../stores/authStore";
import EventCard from "../components/EventCard.vue";

const store = useAuthStore();
const config = useRuntimeConfig();
const toast = useToast();

const events = ref([]);
const loading = ref(true);
const error = ref(null);

// Load events when the component is mounted
onMounted(async () => {
  await fetchEvents();
});

// Fetch events from the backend
const fetchEvents = async () => {
  loading.value = true;
  error.value = null;

  try {
    const response = await fetch(`${config.public.backendUrl}/events/`, {
      headers: {
        'Authorization': `Bearer ${store.session}`
      }
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch events: ${response.status}`);
    }

    const eventsData = await response.json();
    // Process events to include image URLs
    events.value = eventsData.map(event => {
      // For each event, we need to add the default image URL (will be updated when user views details)
      return {
        ...event,
        img_url: `${config.public.backendUrl}/uploads/default-event.jpg` // Use a default image
      };
    });
    console.log('Processed events:', events.value);
  } catch (err) {
    console.error('Error fetching events:', err);
    error.value = 'Failed to load events. Please try again later.';
    toast.add({
      title: 'Error',
      description: error.value,
      color: 'error'
    });
  } finally {
    loading.value = false;
  }
};

// Format date for display
const formatDate = (dateStr) => {
  if (!dateStr) return 'TBD';
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};
</script>
