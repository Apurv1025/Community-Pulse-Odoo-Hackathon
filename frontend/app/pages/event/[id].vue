<template>
    <div class="container mx-auto px-4 py-8">
        <!-- Event Header component -->
        <EventHeader :event_id="eventId" />

        <template v-if="event">
            <!-- Event Details Section -->
            <div class="mt-8 grid grid-cols-1 md:grid-cols-3 gap-8">
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
                                <p class="text-gray-400 whitespace-pre-wrap">{{ event.event_description }}</p>
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
                                        <p class="text-sm text-gray-500">{{ formatDate(event.start_date) }}</p>
                                        <p v-if="event.end_date" class="text-sm text-gray-500">to {{
                                            formatDate(event.end_date) }}</p>
                                    </div>
                                </div>

                                <div class="flex items-start gap-3">
                                    <UIcon name="i-lucide-map-pin" class="w-5 h-5 mt-1 text-primary flex-shrink-0" />
                                    <div>
                                        <h3 class="font-medium">Location</h3>
                                        <p class="text-sm text-gray-500">{{ event.city }}, {{ event.state }}</p>
                                        <p v-if="event.venue" class="text-sm text-gray-500">{{ event.venue }}</p>
                                    </div>
                                </div>

                                <div class="flex items-start gap-3">
                                    <UIcon name="i-lucide-tag" class="w-5 h-5 mt-1 text-primary flex-shrink-0" />
                                    <div>
                                        <h3 class="font-medium">Category</h3>
                                        <p class="text-sm text-gray-500">{{ event.category }}</p>
                                    </div>
                                </div>

                                <div class="flex items-start gap-3">
                                    <UIcon name="i-lucide-user" class="w-5 h-5 mt-1 text-primary flex-shrink-0" />
                                    <div>
                                        <h3 class="font-medium">Organizer</h3>
                                        <p class="text-sm text-gray-500">{{ event.organiser }}</p>
                                        <p v-if="organizerDetails && organizerDetails.email"
                                            class="text-sm text-gray-500">
                                            <UIcon name="i-lucide-mail" class="inline w-3 h-3 mr-1" />
                                            {{ organizerDetails.email }}
                                        </p>
                                        <p v-if="organizerDetails && organizerDetails.phone"
                                            class="text-sm text-gray-500">
                                            <UIcon name="i-lucide-phone" class="inline w-3 h-3 mr-1" />
                                            {{ organizerDetails.phone }}
                                        </p>
                                    </div>
                                </div>
                            </div>

                            <!-- Organizer Actions or Registration Button -->
                            <div v-if="isOrganizer" class="flex gap-2 mt-4">
                                <UButton color="primary" block :to="`/event/update/${eventId}`">
                                    <UIcon name="i-lucide-edit" class="mr-1" />
                                    Edit Event
                                </UButton>
                                <UButton color="error" block type="button" @click="showDeleteModal = true">
                                    <UIcon name="i-lucide-trash-2" class="mr-1" />
                                    Delete
                                </UButton>
                            </div>
                            <template v-else>
                                <UButton v-if="!isRegistered" block color="primary" class="mt-4"
                                    @click="showCountDialog = true">
                                    Register for Event
                                </UButton>
                                <UButton v-else block :color="eventStatusColor" disabled class="mt-4">
                                    {{ eventStatusText }}
                                </UButton>
                            </template>

                            <!-- Attendee Count Dialog -->
                            <UModal v-model="showCountDialog" :ui="{ width: 'sm', container: 'XL' }"
                                :prevent-close="true" @close="showCountDialog = false">
                                <UCard v-if="showCountDialog" @click.stop>
                                    <template #header>
                                        <div class="flex justify-between items-center">
                                            <h3 class="text-base font-semibold leading-6">
                                                How many people will attend?
                                            </h3>
                                        </div>
                                    </template>
                                    <div class="flex flex-col items-center gap-4 py-4" @click.stop>
                                        <p class="text-sm text-gray-500 mb-2">
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

                            <!-- Delete Confirmation Modal -->
                            <UModal v-if="showDeleteModal" v-model="showDeleteModal" :ui="{ container: 'body' }">
                                <UCard class="w-full max-w-md">
                                    <template #header>
                                        <div class="flex items-center">
                                            <UIcon name="i-lucide-alert-triangle" class="w-5 h-5 mr-2 text-red-500" />
                                            <h3 class="text-lg font-medium">Delete Event</h3>
                                        </div>
                                    </template>

                                    <div class="py-4">
                                        <p class="text-gray-400 mb-4">
                                            Are you sure you want to delete <strong class="font-medium">{{
                                                event.event_name }}</strong>?
                                        </p>
                                        <p
                                            class="text-sm text-gray-500 bg-amber-50 p-3 rounded-md border border-amber-200">
                                            <UIcon name="i-lucide-alert-circle"
                                                class="w-4 h-4 inline-block mr-1 text-amber-500" />
                                            This action cannot be undone. All event data including registrations will be
                                            permanently
                                            removed.
                                        </p>
                                    </div>

                                    <template #footer>
                                        <div class="flex justify-end gap-3">
                                            <UButton color="gray" variant="ghost" @click="showDeleteModal = false">
                                                Cancel
                                            </UButton>
                                            <UButton color="error" variant="solid" icon="i-lucide-trash-2"
                                                :loading="isDeleting" @click="deleteEvent">
                                                Delete Event
                                            </UButton>
                                        </div>
                                    </template>
                                </UCard>
                            </UModal>
                        </div>
                    </UCard>
                </div>
            </div>
        </template>

        <!-- Loading State -->
        <div v-else-if="loading" class="flex justify-center items-center h-64">
            <USkeleton class="h-64 w-full" />
        </div>

        <!-- Error State -->
        <UCard v-else class="mt-8 p-6 text-center">
            <UIcon name="i-lucide-alert-triangle" class="w-12 h-12 text-amber-500 mx-auto mb-4" />
            <h2 class="text-xl font-semibold mb-2">Event Not Found</h2>
            <p class="mb-4 text-gray-500">The event you're looking for doesn't exist or has been removed.</p>
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
const isDeleting = ref(false);
const isRegistered = ref(false);
const attendeeCount = ref(1);
const showCountDialog = ref(false);
const showDeleteModal = ref(false);
const organizerDetails = ref(null);
const isOrganizer = computed(() =>
    authStore.user && event.value && authStore.user.username === event.value.organiser
);
const configs = useRuntimeConfig();

// Computed property to determine the status text for registered users
const eventStatusText = computed(() => {
    if (!event.value) return "Already Registered";

    const now = new Date();
    const startDate = new Date(event.value.start_date);
    const endDate = event.value.end_date ? new Date(event.value.end_date) : null;

    // Event has ended
    if (endDate && now > endDate) {
        return "Event Ended";
    }

    // Event is happening now
    if (now >= startDate && (!endDate || now <= endDate)) {
        return "Happening Now";
    }

    // Event is in the future, show countdown
    if (now < startDate) {
        const diffTime = Math.abs(startDate - now);
        const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
        const diffHours = Math.floor((diffTime % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));

        if (diffDays > 0) {
            return `Starts in ${diffDays} day${diffDays > 1 ? 's' : ''}`;
        } else if (diffHours > 0) {
            return `Starts in ${diffHours} hour${diffHours > 1 ? 's' : ''}`;
        } else {
            return "Starting Soon";
        }
    }

    return "Already Registered";
});

// Computed property to determine the status color for registered users
const eventStatusColor = computed(() => {
    if (!event.value) return "gray";

    const now = new Date();
    const startDate = new Date(event.value.start_date);
    const endDate = event.value.end_date ? new Date(event.value.end_date) : null;

    // Event has ended
    if (endDate && now > endDate) {
        return "gray";
    }

    // Event is happening now
    if (now >= startDate && (!endDate || now <= endDate)) {
        return "green";
    }

    // Event is in the future
    return "blue";
});

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

        // Fetch organizer details
        await fetchOrganizerDetails();
    } catch (error) {
        console.error('Error fetching event:', error);
        toast.add({
            title: 'Error',
            description: 'Failed to load event details',
            color: 'error'
        });
    } finally {
        loading.value = false;
    }
};

// Fetch organizer details
const fetchOrganizerDetails = async () => {
    try {
        const response = await fetch(configs.public.backendUrl + `/event/${eventId}/organizer`);
        if (response.ok) {
            const data = await response.json();
            // Make sure we handle missing data gracefully
            organizerDetails.value = {
                username: data.username || event.value?.organiser || 'Unknown',
                email: data.email || '',
                phone: data.phone || ''
            };
        }
    } catch (error) {
        console.error('Error fetching organizer details:', error);
        // Set default values on error
        if (event.value) {
            organizerDetails.value = {
                username: event.value.organiser,
                email: '',
                phone: ''
            };
        }
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
            color: 'error'
        });
    } finally {
        isRegistering.value = false;
    }
};

// This function has been replaced by directly setting showDeleteModal to true in the button

// Delete event
const deleteEvent = async () => {
    isDeleting.value = true;
    try {
        const response = await fetch(configs.public.backendUrl + `/event/delete/${eventId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${authStore.session}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error('Failed to delete event');
        }

        // Close the modal first
        showDeleteModal.value = false;

        // Small delay to ensure modal is fully closed before showing toast
        await new Promise(resolve => setTimeout(resolve, 100));

        toast.add({
            title: 'Success',
            description: 'Event deleted successfully',
            color: 'green'
        });

        // Redirect to home page or events list
        navigateTo('/');
    } catch (error) {
        console.error('Error deleting event:', error);
        toast.add({
            title: 'Error',
            description: error.message || 'Failed to delete event',
            color: 'error'
        });
    } finally {
        isDeleting.value = false;
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