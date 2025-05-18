<template>
    <div>
        <AdminNavbar />
        <UContainer class="py-8">
            <UCard class="w-full max-w-6xl mx-auto">
                <template #header>
                    <div class="flex flex-col gap-1">
                        <h2 class="text-xl font-semibold">Admin Dashboard</h2>
                        <p class="text-sm text-gray-500">Manage event requests</p>
                    </div>
                </template>

                <div v-if="loading" class="flex justify-center py-8">
                    <UButton loading variant="ghost" />
                </div>

                <div v-else-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                    {{ error }}
                </div>

                <div v-else-if="events.length === 0" class="text-center py-10">
                    <p class="text-gray-500 text-xl">No pending event requests</p>
                </div>

                <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-4">
                    <AdminEventCard v-for="event in events" :key="event.id" :event="event" @approve="approveEvent"
                        @reject="rejectEvent" @flag="flagEvent" />
                </div>
            </UCard>
        </UContainer>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useAuthStore } from "../../../stores/authStore";
import AdminEventCard from "../../components/AdminEventCard.vue";
import AdminNavbar from "../../components/AdminNavbar.vue";

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

// Fetch pending event requests from the backend
const fetchEvents = async () => {
    loading.value = true;
    error.value = null;

    try {
        const response = await fetch(`${config.public.backendUrl}/admin/requestevents`, {
            headers: {
                'Authorization': `Bearer ${store.session}`
            }
        });

        if (!response.ok) {
            throw new Error(`Failed to fetch events: ${response.status}`);
        }

        const data = await response.json();
        events.value = data.map(event => ({
            ...event,
            processing: false,
            flagging: false,
            actionType: null
        }));
    } catch (err) {
        console.error('Error fetching events:', err);
        error.value = 'Failed to load event requests. Please try again later.';
        toast.add({
            title: 'Error',
            description: error.value,
            color: 'error'
        });
    } finally {
        loading.value = false;
    }
};

// Approve an event request
const approveEvent = async (eventId) => {
    const event = events.value.find(e => e.id === eventId);
    if (!event) return;

    event.processing = true;
    event.actionType = 'approve';

    try {
        const response = await fetch(`${config.public.backendUrl}/admin/event/accept/${eventId}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${store.session}`
            }
        });

        if (!response.ok) {
            throw new Error(`Failed to approve event: ${response.status}`);
        }

        // Remove the event from the list
        events.value = events.value.filter(e => e.id !== eventId);

        toast.add({
            title: 'Success',
            description: 'Event approved successfully',
            color: 'success'
        });
    } catch (err) {
        console.error('Error approving event:', err);
        toast.add({
            title: 'Error',
            description: 'Failed to approve the event. Please try again.',
            color: 'error'
        });

        // Reset event state
        event.processing = false;
        event.actionType = null;
    }
};

// Reject an event request
const rejectEvent = async (eventId) => {
    const event = events.value.find(e => e.id === eventId);
    if (!event) return;

    event.processing = true;
    event.actionType = 'reject';

    try {
        const response = await fetch(`${config.public.backendUrl}/admin/event/reject/${eventId}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${store.session}`
            }
        });

        if (!response.ok) {
            throw new Error(`Failed to reject event: ${response.status}`);
        }

        // Remove the event from the list
        events.value = events.value.filter(e => e.id !== eventId);

        toast.add({
            title: 'Success',
            description: 'Event rejected successfully',
            color: 'success'
        });
    } catch (err) {
        console.error('Error rejecting event:', err);
        toast.add({
            title: 'Error',
            description: 'Failed to reject the event. Please try again.',
            color: 'error'
        });

        // Reset event state
        event.processing = false;
        event.actionType = null;
    }
};

// Flag an event for further review
const flagEvent = async (eventId) => {
    const event = events.value.find(e => e.id === eventId);
    if (!event) return;

    event.flagging = true;

    try {
        const response = await fetch(`${config.public.backendUrl}/admin/event/flag/${eventId}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${store.session}`
            }
        });

        if (!response.ok) {
            throw new Error(`Failed to flag event: ${response.status}`);
        }

        toast.add({
            title: 'Success',
            description: 'Event flagged for review',
            color: 'blue'
        });
    } catch (err) {
        console.error('Error flagging event:', err);
        toast.add({
            title: 'Error',
            description: 'Failed to flag the event. Please try again.',
            color: 'error'
        });
    } finally {
        // Reset flagging state
        event.flagging = false;
    }
};
</script>