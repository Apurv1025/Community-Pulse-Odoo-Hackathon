<template>
    <nav class="bg-gray-800 p-4">
        <div class="container mx-auto">
            <div class="flex flex-col md:flex-row justify-between items-center">
                <!-- Left section with logo/brand -->
                <div class="flex items-center mb-4 md:mb-0">
                    <NuxtLink to="/" class="text-white text-xl font-bold">Community Pulse</NuxtLink>
                </div>

                <!-- Middle section with search -->
                <div class="w-full md:w-1/3 mb-4 md:mb-0">
                    <form class="flex" @submit.prevent="searchEvents">
                        <input v-model="searchTerm" type="text" placeholder="Search events..."
                            class="w-full px-4 py-2 rounded-l focus:outline-none">
                        <button type="submit"
                            class="bg-blue-500 text-white px-4 py-2 rounded-r hover:bg-blue-600 focus:outline-none">
                            Search
                        </button>
                    </form>
                </div>

                <!-- Right section with event actions and logout -->
                <div class="flex items-center space-x-4">
                    <!-- Conditional Update/Delete links for event organizers -->
                    <template v-if="showEventControls">
                        <NuxtLink :to="`/event/${currentEventId}/update`" class="text-white hover:text-blue-300">
                            Update
                        </NuxtLink>
                        <button class="text-white hover:text-red-300" @click="deleteEvent">
                            Delete
                        </button>
                    </template>

                    <!-- Logout button -->
                    <button class="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600 focus:outline-none"
                        @click="logout">
                        Logout
                    </button>
                </div>
            </div>
        </div>
    </nav>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '../../stores/authStore';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

const searchTerm = ref('');
const currentEventId = ref(null);
const isOrganizer = ref(false);
const currentEvent = ref(null);

// Watch for route changes to determine if we're on an event page
watch(() => route.path, (newPath) => {
    checkIfEventPage(newPath);
}, { immediate: true });

// Check if we're on an event page and set current event id
function checkIfEventPage(path) {
    const eventRegex = /\/event\/([^/]+)(?:\/|$)/;
    const match = path.match(eventRegex);

    if (match && match[1]) {
        currentEventId.value = match[1];
        fetchEventDetails(match[1]);
    } else {
        currentEventId.value = null;
        currentEvent.value = null;
        isOrganizer.value = false;
    }
}

// Fetch event details to determine if current user is organizer
async function fetchEventDetails(eventId) {
    try {
        const config = useRuntimeConfig();
        const { data, error } = await useFetch(
            `${config.public.backendUrl}/events/${eventId}`,
            {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${authStore.session}`
                }
            }
        );

        if (error.value) throw new Error(error.value.message || 'Failed to fetch event');

        currentEvent.value = data.value;
        // Check if current user is the organizer
        isOrganizer.value = data.value.organizer_id === authStore.user?.id;
    } catch (error) {
        console.error('Error fetching event details:', error);
    }
}

// Computed property to determine if event controls should be shown
const showEventControls = computed(() => {
    return currentEventId.value && isOrganizer.value;
});

// Search events
function searchEvents() {
    if (searchTerm.value.trim()) {
        router.push(`/search/${encodeURIComponent(searchTerm.value.trim())}`);
    }
}

// Delete event
async function deleteEvent() {
    if (!currentEventId.value) return;

    if (confirm('Are you sure you want to delete this event?')) {
        try {
            const config = useRuntimeConfig();
            const { error } = await useFetch(
                `${config.public.backendUrl}/events/${currentEventId.value}`,
                {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${authStore.session}`
                    }
                }
            );

            if (error.value) throw new Error(error.value.message || 'Failed to delete event');

            // Redirect to home page after successful deletion
            router.push('/');
        } catch (error) {
            console.error('Error deleting event:', error);
        }
    }
}

// Logout user
function logout() {
    authStore.deleteUserSession();
    router.push('/login');
}
</script>

<style scoped>
/* Additional custom styles can be added here */
</style>