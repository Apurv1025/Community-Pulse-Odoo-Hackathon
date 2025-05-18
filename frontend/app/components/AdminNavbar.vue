<template>
    <nav class="bg-gray-900 p-4">
        <div class="container mx-auto">
            <div class="flex flex-col md:flex-row justify-between items-center">
                <!-- Left section with logo/brand -->
                <div class="flex items-center mb-4 md:mb-0">
                    <NuxtLink to="/" class="text-white text-xl font-bold">Community Pulse Admin</NuxtLink>
                </div>

                <!-- Middle section with event/user search -->
                <div class="w-full md:w-1/2 mb-4 md:mb-0 flex space-x-2">
                    <form class="flex w-1/2" @submit.prevent="searchEvents">
                        <input v-model="searchEventTerm" type="text" placeholder="Search events..."
                            class="w-full px-4 py-2 rounded-l focus:outline-none">
                        <button type="submit"
                            class="bg-blue-500 text-white px-4 py-2 rounded-r hover:bg-blue-600 focus:outline-none">
                            Search Events
                        </button>
                    </form>
                    <form class="flex w-1/2" @submit.prevent="searchUsers">
                        <input v-model="searchUserTerm" type="text" placeholder="Search users..."
                            class="w-full px-4 py-2 rounded-l focus:outline-none">
                        <button type="submit"
                            class="bg-green-500 text-white px-4 py-2 rounded-r hover:bg-green-600 focus:outline-none">
                            Search Users
                        </button>
                    </form>
                </div>

                <!-- Right section with admin actions and logout -->
                <div class="flex items-center space-x-4">
                    <NuxtLink to="/admin/requestevents" class="text-white hover:text-yellow-300">
                        Pending Events
                    </NuxtLink>
                    <NuxtLink to="/admin/users" class="text-white hover:text-yellow-300">
                        Manage Users
                    </NuxtLink>
                    <button class="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600 focus:outline-none"
                        @click="logout">
                        Logout
                    </button>
                </div>
            </div>
        </div>
    </nav>
    <!-- Example: Show fetched results (optional, for demonstration) -->
    <div v-if="showResults" class="bg-gray-100 p-4 mt-2 rounded">
        <div v-if="eventResults.length">
            <h3 class="font-bold mb-2">Event Results:</h3>
            <ul>
                <li v-for="event in eventResults" :key="event.id">{{ event.event_name }}</li>
            </ul>
        </div>
        <div v-if="userResults.length">
            <h3 class="font-bold mb-2">User Results:</h3>
            <ul>
                <li v-for="user in userResults" :key="user.username">{{ user.username }} ({{ user.email }})</li>
            </ul>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../../stores/authStore';

const router = useRouter();
const authStore = useAuthStore();

const searchEventTerm = ref('');
const searchUserTerm = ref('');
const eventResults = ref([]);
const userResults = ref([]);
const showResults = ref(false);

// Fetch events by search term
async function searchEvents() {
    if (searchEventTerm.value.trim()) {
        const config = useRuntimeConfig();
        try {
            const { data, error } = await useFetch(
                `${config.public.backendUrl}/search/${encodeURIComponent(searchEventTerm.value.trim())}`,
                {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${authStore.session}`
                    }
                }
            );
            if (error.value) throw new Error(error.value.message || 'Failed to fetch events');
            eventResults.value = data.value || [];
            userResults.value = [];
            showResults.value = true;
            // Optionally, navigate to a search results page:
            // router.push(`/search/${encodeURIComponent(searchEventTerm.value.trim())}`);
        } catch (err) {
            console.error('Error searching events:', err);
        }
    }
}

// Fetch users by search term (admin)
async function searchUsers() {
    if (searchUserTerm.value.trim()) {
        const config = useRuntimeConfig();
        try {
            const { data, error } = await useFetch(
                `${config.public.backendUrl}/admin/usersearch/${encodeURIComponent(searchUserTerm.value.trim())}`,
                {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${authStore.session}`
                    }
                }
            );
            if (error.value) throw new Error(error.value.message || 'Failed to fetch users');
            userResults.value = data.value || [];
            eventResults.value = [];
            showResults.value = true;
            // Optionally, navigate to a user search results page:
            // router.push(`/admin/usersearch/${encodeURIComponent(searchUserTerm.value.trim())}`);
        } catch (err) {
            console.error('Error searching users:', err);
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
/* Additional custom styles for admin navbar can be added here */
</style>