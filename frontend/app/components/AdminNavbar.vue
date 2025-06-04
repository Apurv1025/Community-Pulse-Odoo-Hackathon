<template>
    <nav class="bg-gray-900 shadow-md p-4">
        <div class="container mx-auto">
            <div class="flex flex-col md:flex-row justify-between items-center">
                <!-- Left section with logo/brand -->
                <div class="flex items-center mb-4 md:mb-0">
                    <NuxtLink to="/" class="text-white text-xl font-bold flex items-center">
                        <UIcon name="i-lucide-shield" class="w-6 h-6 mr-2" />
                        Community Pulse Admin
                    </NuxtLink>
                </div>

                <!-- Middle section with event/user search -->
                <div class="w-full md:w-1/2 mb-4 md:mb-0 flex flex-col sm:flex-row gap-2">
                    <form class="flex w-full sm:w-1/2" @submit.prevent="searchEvents">
                        <div class="flex w-full items-center">
                            <UInput v-model="searchEventTerm" placeholder="Search events..."
                                class="rounded-l-md w-full" />
                            <UButton type="submit" icon="i-lucide-search" color="info" class="rounded-r-md h-full">
                                Events
                            </UButton>
                        </div>
                    </form>
                    <form class="flex w-full sm:w-1/2" @submit.prevent="searchUsers">
                        <div class="flex w-full items-center">
                            <UInput v-model="searchUserTerm" placeholder="Search users..."
                                class="rounded-l-md w-full" />
                            <UButton type="submit" icon="i-lucide-users" color="success" class="rounded-r-md h-full">
                                Users
                            </UButton>
                        </div>
                    </form>
                </div>

                <!-- Right section with admin actions and logout -->
                <div class="flex items-center space-x-4">
                    <UButton to="/admin/users" variant="ghost" color="blue">
                        <UIcon name="i-lucide-users" class="w-5 h-5 mr-1" />
                        <span class="hidden sm:inline">Manage Users</span>
                    </UButton>
                    <UButton color="error" variant="soft" icon="i-lucide-log-out" @click="logout">
                        <span class="hidden sm:inline">Logout</span>
                    </UButton>
                </div>
            </div>
        </div>
    </nav>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../../stores/authStore';

const router = useRouter();
const authStore = useAuthStore();

const searchEventTerm = ref('');
const searchUserTerm = ref('');

// Route to event search results page
function searchEvents() {
    if (searchEventTerm.value.trim()) {
        router.push({
            path: `/search/${encodeURIComponent(searchEventTerm.value.trim())}`,
            query: { q: searchEventTerm.value.trim() }
        });
    }
}

// Route to admin user search results page
function searchUsers() {
    if (searchUserTerm.value.trim()) {
        router.push({
            path: `/admin/usersearch/${encodeURIComponent(searchUserTerm.value.trim())}`,
            query: { q: searchUserTerm.value.trim() }
        });
    }
}

// Logout user
async function logout() {
    await authStore.deleteUserSession();
    router.push('/login');
}
</script>

<style scoped>
/* Additional custom styles for admin navbar can be added here */
</style>