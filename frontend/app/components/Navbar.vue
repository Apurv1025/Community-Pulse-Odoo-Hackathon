<template>
    <nav class="bg-white shadow-md p-4 dark:bg-gray-800">
        <div class="container mx-auto">
            <div class="flex flex-col md:flex-row justify-between items-center">
                <!-- Left section with logo/brand -->
                <div class="flex items-center mb-4 md:mb-0">
                    <NuxtLink to="/" class="text-primary dark:text-white text-xl font-bold flex items-center">
                        <UIcon name="i-lucide-activity" class="w-6 h-6 mr-2" />
                        Community Pulse
                    </NuxtLink>
                </div>

                <!-- Middle section with search -->
                <div class="w-full md:w-1/3 mb-4 md:mb-0">
                    <form class="flex" @submit.prevent="searchEvents">
                        <div class="flex w-full items-center">
                            <UInput v-model="searchTerm" placeholder="Search events..." class="rounded-l-md w-full" />
                            <UButton type="submit" icon="i-lucide-search" color="primary" class="rounded-r-md h-full">
                                Search
                            </UButton>
                        </div>
                    </form>
                </div>

                <!-- Right section with nav actions -->
                <div class="flex items-center space-x-4">
                    <!-- Create Event button visible only to logged-in users -->
                    <UButton v-if="authStore.user" to="/event/create" icon="i-lucide-calendar-plus" class="mr-2"
                        color="primary" variant="soft">
                        Create Event
                    </UButton>

                    <!-- Create Issue button visible only to logged-in users -->
                    <UButton v-if="authStore.user" to="/issue/create" icon="i-lucide-alert-triangle" class="mr-2"
                        color="warning" variant="soft">
                        Report Issue
                    </UButton>

                    <!-- Conditional Update/Delete links for event organizers -->
                    <template v-if="showEventControls">
                        <NuxtLink :to="`/event/${currentEventId}/update`"
                            class="text-primary hover:text-blue-700 dark:text-white dark:hover:text-blue-300">
                            <UIcon name="i-lucide-edit" class="w-5 h-5" />
                            <span class="hidden sm:inline ml-1">Update</span>
                        </NuxtLink>
                        <button class="text-red-500 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300"
                            @click="deleteEvent">
                            <UIcon name="i-lucide-trash-2" class="w-5 h-5" />
                            <span class="hidden sm:inline ml-1">Delete</span>
                        </button>
                    </template>

                    <!-- Logout button -->
                    <UButton v-if="authStore.user" color="error" variant="soft" icon="i-lucide-log-out" @click="logout">
                        <span class="hidden sm:inline">Logout</span>
                    </UButton>
                    <UButton v-else to="/login" color="primary" variant="soft" icon="i-lucide-log-in">
                        <span class="hidden sm:inline">Login</span>
                    </UButton>
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
        router.push({
            path: `/search/${encodeURIComponent(searchTerm.value.trim())}`,
            query: { q: searchTerm.value.trim() }
        });
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
async function logout() {
    await authStore.deleteUserSession();
    router.push('/login');
}
</script>

<style scoped>
/* Additional custom styles can be added here */
</style>