<template>
    <div class="container mx-auto px-4 py-8">
        <h1 class="text-3xl font-bold mb-6 text-indigo-800">Search Results for "{{ searchTerm }}"</h1>

        <!-- Loading state -->
        <div v-if="isLoading" class="flex justify-center items-center h-64">
            <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500" />
        </div>

        <!-- Error state -->
        <div v-else-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            <p>{{ error }}</p>
        </div>

        <!-- No results state -->
        <div v-else-if="events && events.length === 0" class="text-center py-10">
            <p class="text-xl text-gray-600">No events found matching "{{ searchTerm }}"</p>
            <NuxtLink to="/"
                class="mt-4 inline-block bg-indigo-600 text-white px-6 py-2 rounded-md hover:bg-indigo-700 transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2">
                View All Events
            </NuxtLink>
        </div>

        <!-- Results grid -->
        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <EventCard v-for="event in events" :key="event.id" :event-name="event.event_name || ''"
                :event-date="formatDate(event.start_date)"
                :event-location="event.address + ', ' + event.city + ', ' + event.state"
                :event-img="event.img_url || ''" :event-url="`/event/${event.id}`"
                :event-type="event.category || 'General'" :event-description="event.event_description || ''" />
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { useAuthStore } from '../../../stores/authStore';

const route = useRoute();
const authStore = useAuthStore();

// Get search term from route params
const searchTerm = ref(route.params.searchterm || '');

// State variables
const events = ref([]);
const isLoading = ref(true);
const error = ref(null);

// Format date for display
function formatDate(dateString) {
    if (!dateString) return 'Date not specified';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Fetch events based on search term
async function fetchSearchResults() {
    isLoading.value = true;
    error.value = null;

    try {
        const config = useRuntimeConfig();
        const { data, error: fetchError } = await useFetch(
            `${config.public.backendUrl}/search/${encodeURIComponent(searchTerm.value)}`,
            {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${authStore.session}`
                }
            }
        );

        if (fetchError.value) {
            throw new Error(fetchError.value.message || 'Failed to fetch search results');
        }

        console.log('Search results:', data.value); // Debug: Log the API response
        events.value = data.value || [];
    } catch (err) {
        console.error('Error fetching search results:', err);
        error.value = 'Failed to load search results. Please try again.';
    } finally {
        isLoading.value = false;
    }
}

// Fetch events when component is mounted
onMounted(() => {
    fetchSearchResults();
});
</script>

<style scoped>
.line-clamp-3 {
    display: -webkit-box;
    -webkit-line-clamp: 3;
    line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
}
</style>