<template>
    <div class="container mx-auto px-4 py-8">
        <!-- Event Header component -->
        <EventHeader :event_id="eventId" />

        <template v-if="event">
            <!-- Event Details Section -->
            <div class="mt-8 grid grid-cols-1 md:grid-cols-3 gap-8">
                <!-- Left Column - Event Images Carousel -->
                <div class="md:col-span-2">
                    <UCard class="overflow-hidden">
                        <!-- Image Carousel if multiple images are available -->
                        <div v-if="eventImages.length > 0" class="w-full aspect-video">
                            <UCarousel v-slot="{ item }" :items="eventImages" dots class="w-full aspect-video">
                                <img :src="item" :alt="event.event_name" class="w-full h-full object-cover rounded-lg">
                            </UCarousel>
                        </div>
                        <div v-else class="w-full aspect-video bg-gray-200 flex items-center justify-center">
                            <UIcon name="i-lucide-image" class="w-16 h-16 text-gray-400" />
                        </div>

                        <div class="p-4">
                            <h1 class="text-2xl md:text-3xl font-bold mb-4">{{ event.event_name }}</h1>

                            <!-- Event Description -->
                            <div class="mt-6">
                                <h2 class="text-xl font-semibold mb-2">About this event</h2>
                                <p class="text-gray-400 whitespace-pre-wrap">{{ event.event_description ||
                                    'No description provided' }}</p>
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
                                        <p v-if="event.address" class="text-sm text-gray-500">{{ event.address }}</p>
                                    </div>
                                </div>

                                <div class="flex items-start gap-3">
                                    <UIcon name="i-lucide-tag" class="w-5 h-5 mt-1 text-primary flex-shrink-0" />
                                    <div>
                                        <h3 class="font-medium">Category</h3>
                                        <p class="text-sm text-gray-500">{{ event.category }}</p>
                                    </div>
                                </div>

                                <!-- Event Type (Free/Paid) -->
                                <div class="flex items-start gap-3">
                                    <UIcon name="i-lucide-ticket" class="w-5 h-5 mt-1 text-primary flex-shrink-0" />
                                    <div>
                                        <h3 class="font-medium">Event Type</h3>
                                        <p class="text-sm text-gray-500">{{ event.type }}</p>
                                    </div>
                                </div>

                                <!-- Max Capacity -->
                                <div v-if="event.max_capacity" class="flex items-start gap-3">
                                    <UIcon name="i-lucide-users" class="w-5 h-5 mt-1 text-primary flex-shrink-0" />
                                    <div>
                                        <h3 class="font-medium">Max Capacity</h3>
                                        <p class="text-sm text-gray-500">{{ event.max_capacity }} attendees</p>
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
                                    @click="handleRegistrationClick">
                                    {{ event.type === 'paid' ? 'Buy Tickets' : 'Register for Event' }}
                                </UButton>
                                <UButton v-else block :color="eventStatusColor" disabled class="mt-4">
                                    {{ eventStatusText }}
                                </UButton>
                            </template>

                            <!-- Tier Selection Dialog for Paid Events -->
                            <UModal v-model="showTierDialog" :ui="{ width: 'sm', container: 'XL' }" class="mt-4"
                                :prevent-close="true" @close="showTierDialog = false">
                                <UCard v-if="showTierDialog" @click.stop>
                                    <template #header>
                                        <div class="flex justify-between items-center">
                                            <h3 class="text-base font-semibold leading-6">
                                                Select Ticket Tier
                                            </h3>
                                        </div>
                                    </template>
                                    <div class="flex flex-col gap-4 py-4" @click.stop="$event.stopPropagation()">
                                        <div v-if="tiers.length === 0" class="text-center text-gray-500">
                                            No tickets available for this event
                                        </div>
                                        <div v-for="tier in tiers" :key="tier.id"
                                            class="border rounded-lg p-4 cursor-pointer hover:bg-gray-50"
                                            :class="{ 'border-primary bg-primary-50': selectedTierId === tier.id }"
                                            @click.stop="selectedTierId = tier.id">
                                            <div class="flex items-center justify-between mb-2">
                                                <div class="flex items-center gap-2">
                                                    <input :id="`tier-${tier.id}`" v-model="selectedTierId" type="radio"
                                                        :value="tier.id" class="text-primary" @click.stop>
                                                    <label :for="`tier-${tier.id}`" class="font-medium">
                                                        {{ tier.tier_name }}
                                                    </label>
                                                </div>
                                                <span class="font-bold text-primary">₹{{ tier.tier_price }}</span>
                                            </div>
                                            <p class="text-sm text-gray-500 mb-2">{{ tier.description ||
                                                'Standard ticket' }}</p>
                                            <div class="flex items-center justify-between text-xs">
                                                <span class="text-gray-400">{{ tier.leftover }} tickets left</span>
                                                <span v-if="tier.max_tickets_per_person" class="text-gray-400">
                                                    Max {{ tier.max_tickets_per_person }} per person
                                                </span>
                                            </div>
                                        </div>
                                        <div v-if="selectedTierId" class="mt-4">
                                            <label class="block text-sm font-medium mb-2">Number of Tickets</label>
                                            <UInput v-model="selectedQuantity" type="number" min="1"
                                                :max="getMaxQuantityForTier(selectedTierId)" size="lg" class="w-full"
                                                @click="handleInputClick" />
                                            <div class="mt-2 text-sm text-gray-500">
                                                Total: ₹{{ getTotalAmount() }}
                                            </div>
                                        </div>
                                    </div>
                                    <template #footer>
                                        <div class="flex justify-end gap-3">
                                            <UButton color="gray" variant="ghost" @click="showTierDialog = false">
                                                Cancel
                                            </UButton>
                                            <UButton color="primary" :loading="isPaymentProcessing"
                                                :disabled="!selectedTierId || selectedQuantity < 1"
                                                @click="initiatePayment">
                                                Pay ₹{{ getTotalAmount() }}
                                            </UButton>
                                        </div>
                                    </template>
                                </UCard>
                            </UModal>

                            <!-- Attendee Count Dialog -->
                            <UModal v-model="showCountDialog" :ui="{ width: 'sm', container: 'XL' }" class="mt-4"
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
                            <UModal v-if="showDeleteModal" v-model="showDeleteModal" class="mt-4"
                                :ui="{ container: 'body' }">
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

                            <!-- Map -->
                            <LMap class="mt-4 rounded-2xl" style="height: 350px" :zoom="6" :center="latLong"
                                :use-global-leaflet="false">
                                <LTileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                                    attribution="&amp;copy; <a href=&quot;https://www.openstreetmap.org/&quot;>OpenStreetMap</a> contributors"
                                    layer-type="base" name="OpenStreetMap" />
                                <LMarker :lat-lng="latLong" />
                            </LMap>

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
const config = useRuntimeConfig();

// Data
const event = ref(null);
const eventImages = ref(['https://picsum.photos/800/400', 'https://picsum.photos/800/401', 'https://picsum.photos/800/402']);
const loading = ref(true);
const isRegistering = ref(false);
const isDeleting = ref(false);
const isRegistered = ref(false);
const attendeeCount = ref(1);
const showCountDialog = ref(false);
const showDeleteModal = ref(false);
const organizerDetails = ref(null);
const latLong = ref([19.091651970649906, 72.86280672834073]); // Default coordinates for Mumbai
const tiers = ref([]);
const selectedTierId = ref(null);
const showTierDialog = ref(false);
const isPaymentProcessing = ref(false);
const selectedQuantity = ref(1);

// Computed properties
const isOrganizer = computed(() =>
    authStore.user && event.value && authStore.user.username === event.value.organiser
);

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
        const response = await fetch(config.public.backendUrl + `/event/${eventId}`);
        if (!response.ok) {
            throw new Error('Failed to fetch event details');
        }

        // Parse the new response format with event and images
        const data = await response.json();
        console.log("Full API response:", data);
        event.value = data.event;

        // Process images and create URLs
        if (data.images && Array.isArray(data.images) && data.images.length > 0) {
            console.log("Raw image data:", data.images);
            // Create image URLs based on backend URL pattern
            eventImages.value = data.images.map(imageName =>
                `${config.public.backendUrl}/uploads/${imageName}`
            );
            console.log("Image URLs created:", eventImages.value);
        } else {
            // Use placeholder images if no images are available
            eventImages.value = [
                'https://picsum.photos/640/360?random=1',
                'https://picsum.photos/640/360?random=2'
            ];
            console.log("Using placeholder images");
        }

        // Set map location based on event coordinates
        if (event.value.latitude && event.value.longitude) {
            latLong.value = [
                parseFloat(event.value.latitude),
                parseFloat(event.value.longitude)
            ];
        }

        // Check if user is already registered
        await checkRegistrationStatus();

        // Fetch organizer details
        await fetchOrganizerDetails();

        // If this is a paid event, fetch tiers
        if (event.value.type === "paid") {
            await fetchEventTiers();
        }
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
        const response = await fetch(config.public.backendUrl + `/event/${eventId}/organizer`);
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

// Fetch event tiers for paid events
const fetchEventTiers = async () => {
    try {
        console.log('Fetching tiers for event:', eventId);
        const response = await fetch(config.public.backendUrl + `/event/${eventId}/tiers`);
        if (response.ok) {
            const data = await response.json();
            console.log('Tiers response:', data);

            if (data && Array.isArray(data) && data.length > 0) {
                tiers.value = data.filter(tier => tier.leftover > 0); // Only show tiers with available tickets
                console.log('Filtered tiers with available tickets:', tiers.value);

                // If we have tiers, select the first one by default
                if (tiers.value.length > 0) {
                    selectedTierId.value = tiers.value[0].id;
                    console.log('Selected first tier:', tiers.value[0]);
                }
            } else {
                console.warn('No tiers returned from API or invalid response format');
            }
        } else {
            console.error('Error fetching tiers, status:', response.status);
        }
    } catch (error) {
        console.error('Error fetching event tiers:', error);
        toast.add({
            title: 'Warning',
            description: 'Failed to load ticket options',
            color: 'amber'
        });
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

        const response = await fetch(config.public.backendUrl + `/event/${eventId}/registered`, {
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

// Handle registration button click
const handleRegistrationClick = () => {
    console.log('Registration button clicked');
    console.log('Event:', event.value);
    console.log('Event type:', event.value?.type);
    console.log('Available tiers:', tiers.value);
    console.log('Tiers length:', tiers.value?.length);

    if (!authStore.session) {
        toast.add({
            title: 'Authentication Required',
            description: 'Please log in to register for events',
            color: 'amber'
        });
        return;
    }

    // Check if event type is paid (case insensitive)
    const eventType = event.value?.type?.toLowerCase();
    console.log('Event type (lowercase):', eventType);

    if (eventType === 'paid') {
        console.log('Event is paid, checking tiers...');
        if (tiers.value.length === 0) {
            console.log('No tiers available');
            // Re-fetch tiers just in case
            fetchEventTiers().then(() => {
                console.log('Re-fetched tiers:', tiers.value);
                if (tiers.value.length === 0) {
                    toast.add({
                        title: 'No Tickets Available',
                        description: 'Sorry, there are no tickets available for this event',
                        color: 'amber'
                    });
                } else {
                    console.log('Tiers found after re-fetch, opening tier dialog');
                    showTierDialog.value = true;
                }
            });
            return;
        }
        console.log('Opening tier dialog');
        showTierDialog.value = true;
    } else {
        console.log('Event is free, opening count dialog');
        showCountDialog.value = true;
    }
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

        const response = await fetch(config.public.backendUrl + `/event/${eventId}/register`, {
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

// Delete event
const deleteEvent = async () => {
    isDeleting.value = true;
    try {
        const response = await fetch(config.public.backendUrl + `/event/delete/${eventId}`, {
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

// Get maximum quantity for selected tier
const getMaxQuantityForTier = (tierId) => {
    const tier = tiers.value.find(t => t.id === tierId);
    if (!tier) return 1;

    const maxFromLeftover = tier.leftover;
    const maxFromPersonLimit = tier.max_tickets_per_person || 10;

    return Math.min(maxFromLeftover, maxFromPersonLimit);
};

// Calculate total amount
const getTotalAmount = () => {
    if (!selectedTierId.value || !selectedQuantity.value) return 0;

    const tier = tiers.value.find(t => t.id === selectedTierId.value);
    if (!tier) return 0;

    return tier.tier_price * selectedQuantity.value;
};

// Initiate Razorpay payment
const initiatePayment = async () => {
    if (!selectedTierId.value || selectedQuantity.value < 1) {
        toast.add({
            title: 'Error',
            description: 'Please select a tier and quantity',
            color: 'error'
        });
        return;
    }

    isPaymentProcessing.value = true;

    try {
        // Generate order from backend using the correct endpoint
        const orderResponse = await fetch(
            `${config.public.backendUrl}/razorpay/create_order?tier_id=${selectedTierId.value}&quantity=${selectedQuantity.value}`,
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${authStore.session}`
                }
            }
        );

        if (!orderResponse.ok) {
            throw new Error('Failed to create payment order');
        }

        const orderData = await orderResponse.json();
        console.log('Order response:', orderData);

        // Extract order ID and amount from response
        const orderId = orderData.id;
        const amount = orderData.amount;

        console.log('Order ID for Razorpay:', orderId);

        // Load Razorpay script if not already loaded
        if (!window.Razorpay) {
            await new Promise((resolve, reject) => {
                const script = document.createElement('script');
                script.src = 'https://checkout.razorpay.com/v1/checkout.js';
                script.onload = resolve;
                script.onerror = reject;
                document.body.appendChild(script);
            });
        }

        const options = {
            key: config.public.razorpayKey,
            order_id: orderId, // This is the required format for Razorpay
            amount: amount,  // amount in paise from the server
            currency: 'INR',
            name: event.value.event_name,
            description: `Ticket for ${event.value.event_name}`,
            image: event.value.image_url || '', // Event logo/image if available
            handler: function (response) {
                processPaymentResponse(response);
            },
            prefill: {
                name: authStore.user?.username || 'Customer',
                email: authStore.user?.email || '',
                contact: authStore.user?.phone || '',
            },
            notes: {
                event_id: eventId,
                tier_id: selectedTierId.value,
                quantity: selectedQuantity.value
            },
            theme: {
                color: '#3498db' // Use your primary color
            },
            modal: {
                ondismiss: function () {
                    isPaymentProcessing.value = false;
                }
            }
        };

        const rzp1 = new window.Razorpay(options);

        // Handle payment failures
        rzp1.on('payment.failed', function (response) {
            console.error('Payment failed:', response.error);
            isPaymentProcessing.value = false;
            toast.add({
                title: 'Payment Failed',
                description: response.error.description || 'Transaction was unsuccessful',
                color: 'error'
            });
        });

        // Open Razorpay checkout
        rzp1.open();

    } catch (error) {
        console.error('Payment initiation error:', error);
        toast.add({
            title: 'Payment Failed',
            description: error.message || 'Failed to initiate payment',
            color: 'error'
        });
        isPaymentProcessing.value = false;
    }
};

// Process payment response from Razorpay
const processPaymentResponse = async (response) => {
    try {
        // Log payment response for debugging
        console.log('Razorpay payment response:', response);

        // Verify payment on backend
        const paymentId = encodeURIComponent(response.razorpay_payment_id);
        const orderId = encodeURIComponent(response.razorpay_order_id);
        const signature = encodeURIComponent(response.razorpay_signature);

        console.log('Payment verification data:', {
            paymentId,
            orderId,
            signature
        });

        const verifyResponse = await fetch(
            `${config.public.backendUrl}/razorpay/verify_payment?payment_id=${paymentId}&order_id=${orderId}&signature=${signature}`,
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${authStore.session}`
                },
                // Additional data in body if needed
                body: JSON.stringify({
                    event_id: eventId,
                    tier_id: selectedTierId.value,
                    quantity: selectedQuantity.value
                }),
            });

        if (verifyResponse.ok) {
            showTierDialog.value = false;
            isRegistered.value = true;

            // Refresh event details to update tier leftover counts
            await fetchEventTiers();

            toast.add({
                title: 'Payment Successful!',
                description: `You have successfully purchased ${selectedQuantity.value} ticket(s)`,
                color: 'green'
            });
        } else {
            throw new Error('Payment verification failed');
        }
    } catch (error) {
        console.error('Payment verification error:', error);
        toast.add({
            title: 'Payment Verification Failed',
            description: 'Please contact support if amount was deducted',
            color: 'error'
        });
    } finally {
        isPaymentProcessing.value = false;
    }
};

// Fetch data on page load
onMounted(() => {
    fetchEventDetails();
});
</script>