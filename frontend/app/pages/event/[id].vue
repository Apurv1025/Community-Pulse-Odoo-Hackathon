<template>
    <div class="container mx-auto px-4 py-8">
        <!-- Event Header component -->
        <EventHeader :event_id="eventId" />

        <!-- Event Details Section -->
        <div v-if="event" class="mt-8 grid grid-cols-1 md:grid-cols-3 gap-8">
            <!-- Left Column - Event Image -->
            <div class="md:col-span-2">
                <UCard class="overflow-hidden">
                    <div v-if="event.img_url" class="w-full aspect-video">
                        <img :src="event.img_url" :alt="event.event_name" class="w-full h-full object-cover">
                    </div>
                    <div v-else class="w-full aspect-video bg-gray-200 flex items-center justify-center">
                        <UIcon name="i-lucide-image" class="w-16 h-16 text-gray-400" />
                    </div>

                    <div class="p-4">
                        <h1 class="text-2xl md:text-3xl font-bold mb-4">{{ event.event_name }}</h1>

                        <!-- Event Description -->
                        <div class="mt-6">
                            <h2 class="text-xl font-semibold mb-2">About this event</h2>
                            <p class="text-gray-700 whitespace-pre-wrap">{{ event.event_description }}</p>
                        </div>
                    </div>
                </UCard>
            </div>

            <!-- Right Column - Event Information -->
            <div class="md:col-span-1">
                <UCard class="mb-6">
                    <div class="p-4">
                        <!-- Event Details -->
                        <div class="flex flex-col gap-4 mb-6">
                            <div class="flex items-start gap-3">
                                <UIcon name="i-lucide-calendar" class="w-5 h-5 mt-1 text-primary flex-shrink-0" />
                                <div>
                                    <h3 class="font-medium">Date and Time</h3>
                                    <p class="text-sm text-gray-600">{{ formatDate(event.start_date) }}</p>
                                    <p v-if="event.end_date" class="text-sm text-gray-600">to {{
                                        formatDate(event.end_date) }}</p>
                                </div>
                            </div>

                            <div class="flex items-start gap-3">
                                <UIcon name="i-lucide-map-pin" class="w-5 h-5 mt-1 text-primary flex-shrink-0" />
                                <div>
                                    <h3 class="font-medium">Location</h3>
                                    <p class="text-sm text-gray-600">{{ event.city }}, {{ event.state }}</p>
                                    <p v-if="event.venue" class="text-sm text-gray-600">{{ event.venue }}</p>
                                </div>
                            </div>

                            <div class="flex items-start gap-3">
                                <UIcon name="i-lucide-tag" class="w-5 h-5 mt-1 text-primary flex-shrink-0" />
                                <div>
                                    <h3 class="font-medium">Category</h3>
                                    <p class="text-sm text-gray-600">{{ event.category }}</p>
                                </div>
                            </div>

                            <div class="flex items-start gap-3">
                                <UIcon name="i-lucide-user" class="w-5 h-5 mt-1 text-primary flex-shrink-0" />
                                <div>
                                    <h3 class="font-medium">Organizer</h3>
                                    <p class="text-sm text-gray-600">{{ event.organiser }}</p>
                                </div>
                            </div>
                        </div>

                        <!-- Registration/RSVP Button -->
                        <UButton v-if="!isRegistered" block color="primary" class="mt-4"
                            @click="showCountDialog = true">
                            Register for Event
                        </UButton>
                        <UButton v-else block color="gray" disabled class="mt-4">
                            Already Registered
                        </UButton>

                        <!-- Attendee Count Dialog -->
                        <UModal v-model="showCountDialog" :ui="{ width: 'sm', container: 'XL' }" :prevent-close="true"
                            @close="showCountDialog = false">
                            <UCard v-if="showCountDialog" @click.stop>
                                <template #header>
                                    <div class="flex justify-between items-center">
                                        <h3 class="text-base font-semibold leading-6">
                                            How many people will attend?
                                        </h3>
                                    </div>
                                </template>
                                <div class="flex flex-col items-center gap-4 py-4" @click.stop>
                                    <p class="text-sm text-gray-600 mb-2">
                                        Please select the number of attendees
                                    </p>
                                    <div class="w-1/2" @click.stop @mousedown.stop @blur.stop>
                                        <UInput v-model="attendeeCount" type="number" min="1" :max="10" size="lg"
                                            class="w-full" @click="handleInputClick" @blur.stop @focus.stop />
                                    </div>
                                </div>
                                <template #footer>
                                    <div class="flex justify-end gap-3">
                                        <UButton color="gray" variant="ghost" @click="showCountDialog = false">
                                            Cancel
                                        </UButton>
                                        <UButton color="primary" :loading="isRegistering" @click="registerForEvent">
                                            Confirm Registration
                                        </UButton>
                                    </div>
                                </template>
                            </UCard>
                        </UModal>

                        <!-- Share Button -->
                        <UButton block variant="outline" color="gray" icon="i-lucide-share-2" class="mt-3"
                            @click="shareEvent">
                            Share Event
                        </UButton>
                    </div>
                </UCard>
            </div>
        </div>

        <!-- Loading State -->
        <div v-else-if="loading" class="flex justify-center items-center h-64">
            <USkeleton class="h-64 w-full" />
        </div>

        <!-- Error State -->
        <UCard v-else class="mt-8 p-6 text-center">
            <UIcon name="i-lucide-alert-triangle" class="w-12 h-12 text-amber-500 mx-auto mb-4" />
            <h2 class="text-xl font-semibold mb-2">Event Not Found</h2>
            <p class="mb-4 text-gray-600">The event you're looking for doesn't exist or has been removed.</p>
            <UButton to="/" icon="i-lucide-home">Back to Home</UButton>
        </UCard>
    </div>
</template>

<script setup>
import { useAuthStore } from '../stores/authStore';

const route = useRoute();
const eventId = route.params.id;
const toast = useToast();
const authStore = useAuthStore();

// Data
const event = ref(null);
const loading = ref(true);
const isRegistering = ref(false);
const isRegistered = ref(false);
const attendeeCount = ref(1);
const showCountDialog = ref(false);
const configs = useRuntimeConfig();

// Fetch event details
const fetchEventDetails = async () => {
    loading.value = true;
    try {
        // Replace with your actual API endpoint
        const response = await fetch(configs.public.backendUrl + `/event/${eventId}`);
        if (!response.ok) {
            throw new Error('Failed to fetch event details');
        }
        event.value = await response.json();

        // Check if user is already registered
        await checkRegistrationStatus();
    } catch (error) {
        console.error('Error fetching event:', error);
        toast.add({
            title: 'Error',
            description: 'Failed to load event details',
            color: 'red'
        });
    } finally {
        loading.value = false;
    }
};

// Check if user is registered for the event
const checkRegistrationStatus = async () => {
    try {
        const token = authStore.session;
        if (!token) {
            // User is not authenticated, so they can't be registered
            isRegistered.value = false;
            return;
        }

        const response = await fetch(configs.public.backendUrl + `/event/${eventId}/registered`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            const data = await response.json();
            isRegistered.value = data.registered || false;
        }
    } catch (error) {
        console.error('Error checking registration status:', error);
    }
};

// Format date
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

// Handle input click to prevent unwanted modal triggers
const handleInputClick = (event) => {
    event.stopPropagation();
    event.preventDefault();
    // Make sure the event doesn't propagate up to parent elements
    return false;
};

// Register for event
const registerForEvent = async (event) => {
    // Prevent any default behavior and stop event propagation
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }

    isRegistering.value = true;
    try {
        const token = authStore.session;
        if (!token) {
            throw new Error('You must be logged in to register for events');
        }

        // Close dialog
        showCountDialog.value = false;

        const response = await fetch(configs.public.backendUrl + `/event/${eventId}/register`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                count: parseInt(attendeeCount.value) || 1
            })
        });

        if (!response.ok) throw new Error('Registration failed');

        isRegistered.value = true;

        // Ensure dialog remains closed
        showCountDialog.value = false;

        // Small delay to ensure modal is fully closed before showing toast
        await new Promise(resolve => setTimeout(resolve, 100));

        toast.add({
            title: 'Success',
            description: 'You have registered for this event!',
            color: 'green'
        });
    } catch (error) {
        toast.add({
            title: 'Registration Failed',
            description: error.message || 'Something went wrong',
            color: 'red'
        });
    } finally {
        isRegistering.value = false;
    }
};

// Share event
const shareEvent = async () => {
    if (navigator.share) {
        try {
            await navigator.share({
                title: event.value.event_name,
                text: `Check out this event: ${event.value.event_name}`,
                url: window.location.href
            });
        } catch (error) {
            if (error.name !== 'AbortError') {
                toast.add({
                    title: 'Sharing Failed',
                    description: 'Could not share this event',
                    color: 'amber'
                });
            }
        }
    } else {
        // Fallback - copy link to clipboard
        navigator.clipboard.writeText(window.location.href);
        toast.add({
            title: 'Link Copied',
            description: 'Event link copied to clipboard',
            color: 'green'
        });
    }
};

// Fetch data on page load
onMounted(() => {
    fetchEventDetails();
});
</script>