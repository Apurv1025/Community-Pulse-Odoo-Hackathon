<script setup lang="ts">
import { useAuthStore } from "../../../stores/authStore";

const store = useAuthStore();
const router = useRouter();
const config = useRuntimeConfig();
const toast = useToast();

const state = reactive({
    event_name: '',
    event_description: '',
    start_date: '',
    end_date: '',
    category: '',
    event_type: 'Free', // Default to Free
    registration_start: '',
    registration_end: '',
    address: '',
    city: '',
    state: '',
    latitude: '',
    longitude: '',
    max_capacity: '',
    error: '',
    isLoading: false,
    locationLoading: false,
    showFileUpload: false,
    showTierSetup: false, // New field to control tier setup visibility
    createdEventId: null
});

// New reactive object for pricing tiers
const tiers = reactive({
    items: [{ tier_name: 'General Admission', price: 0, quantity: 0 }], // Default tier
    error: '',
    isLoading: false
});

// Track remaining capacity for tiers
const remainingCapacity = computed(() => {
    const maxCapacity = parseInt(state.max_capacity) || 0;
    const usedCapacity = tiers.items.reduce((total, tier) => total + (parseInt(tier.quantity) || 0), 0);
    return maxCapacity - usedCapacity;
});

// Add a new tier
const addTier = () => {
    tiers.items.push({ tier_name: '', price: 0, quantity: 0 });
};

// Remove a tier
const removeTier = (index) => {
    tiers.items.splice(index, 1);
    // Always keep at least one tier
    if (tiers.items.length === 0) {
        tiers.items.push({ tier_name: 'General Admission', price: 0, quantity: 0 });
    }
};

// Function to save tiers to the backend
const saveTiers = async () => {
    tiers.isLoading = true;
    tiers.error = '';

    // Validate tiers
    if (remainingCapacity.value !== 0) {
        tiers.error = remainingCapacity.value < 0
            ? 'Total tier quantity exceeds the maximum event capacity.'
            : 'Total tier quantity must exactly match the maximum event capacity.';
        tiers.isLoading = false;
        toast.add({
            title: 'Validation Error',
            description: tiers.error,
            color: 'error'
        });
        return;
    }

    // Validate that all tiers have names and positive quantities
    for (const tier of tiers.items) {
        if (!tier.tier_name.trim()) {
            tiers.error = 'All tiers must have names.';
            tiers.isLoading = false;
            toast.add({
                title: 'Validation Error',
                description: tiers.error,
                color: 'error'
            });
            return;
        }

        if (parseInt(tier.quantity) <= 0) {
            tiers.error = 'All tiers must have a positive quantity.';
            tiers.isLoading = false;
            toast.add({
                title: 'Validation Error',
                description: tiers.error,
                color: 'error'
            });
            return;
        }

        if (state.event_type === 'Paid' && parseFloat(tier.price) <= 0) {
            tiers.error = 'All tiers must have a positive price for paid events.';
            tiers.isLoading = false;
            toast.add({
                title: 'Validation Error',
                description: tiers.error,
                color: 'error'
            });
            return;
        }
    }

    try {
        // Send each tier individually to the backend
        const results = [];
        for (const tier of tiers.items) {
            // Create the tier data in the required schema format
            const tierData = {
                tier_name: tier.tier_name,
                tier_price: parseFloat(tier.price) || 0,
                quantity: parseInt(tier.quantity) || 0
            };

            console.log('Posting tier:', tierData);

            // Make API call for each tier
            const response = await fetch(`${config.public.backendUrl}/event/${state.createdEventId}/tiers`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${store.session}`
                },
                body: JSON.stringify(tierData)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `Failed to save tier: ${tier.tier_name}`);
            }

            const result = await response.json();
            results.push(result);
        }

        console.log('All tiers saved:', results);

        toast.add({
            title: 'Success',
            description: 'Pricing tiers saved successfully.',
            color: 'success'
        });

        // Move to image upload step
        state.showTierSetup = false;
        state.showFileUpload = true;
    } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Failed to save pricing tiers.';
        tiers.error = errorMessage;
        toast.add({
            title: 'Error',
            description: tiers.error,
            color: 'error'
        });
    } finally {
        tiers.isLoading = false;
    }
};

// Default categories list
const categories = ref([
    'Garage Sales',
    'Sports Matches',
    'Community Classes',
    'Volunteer Opportunities',
    'Exhibitions',
    'Small Festivals or Celebrations',
    'Other'
]);

// Get user's current location
const getCurrentLocation = () => {
    if (!navigator.geolocation) {
        toast.add({
            title: 'Error',
            description: 'Geolocation is not supported by your browser',
            color: 'error'
        });
        return;
    }

    state.locationLoading = true;
    navigator.geolocation.getCurrentPosition(
        (position) => {
            state.latitude = position.coords.latitude.toString();
            state.longitude = position.coords.longitude.toString();
            state.locationLoading = false;
            toast.add({
                title: 'Success',
                description: 'Location successfully captured',
                color: 'success'
            });
        },
        (error) => {
            state.locationLoading = false;
            let errorMsg = 'Failed to get your location';
            switch (error.code) {
                case error.PERMISSION_DENIED:
                    errorMsg = 'Location permission denied';
                    break;
                case error.POSITION_UNAVAILABLE:
                    errorMsg = 'Location information unavailable';
                    break;
                case error.TIMEOUT:
                    errorMsg = 'The request to get location timed out';
                    break;
            }
            toast.add({
                title: 'Error',
                description: errorMsg,
                color: 'error'
            });
        }
    );
};

const createEvent = async () => {
    state.isLoading = true;
    state.error = '';

    // Validate dates
    const startDate = new Date(state.start_date);
    const endDate = new Date(state.end_date);
    const regStartDate = new Date(state.registration_start);
    const regEndDate = new Date(state.registration_end);

    if (endDate < startDate) {
        state.error = 'End date cannot be before start date';
        state.isLoading = false;
        toast.add({
            title: 'Validation Error',
            description: state.error,
            color: 'error'
        });
        return;
    }

    if (regEndDate < regStartDate) {
        state.error = 'Registration end date cannot be before registration start date';
        state.isLoading = false;
        toast.add({
            title: 'Validation Error',
            description: state.error,
            color: 'error'
        });
        return;
    }

    // Validate latitude and longitude
    if (!state.latitude || !state.longitude) {
        state.error = 'Latitude and longitude are required. Use the "Get Current Location" button or enter them manually.';
        state.isLoading = false;
        toast.add({
            title: 'Validation Error',
            description: state.error,
            color: 'error'
        });
        return;
    }

    try {
        // Create an event object matching the backend EventCreate model
        const eventData = {
            event_name: state.event_name,
            event_description: state.event_description,
            start_date: state.start_date,
            end_date: state.end_date,
            category: state.category,
            type: state.event_type, // Send as 'type' to the server
            registration_start: state.registration_start,
            registration_end: state.registration_end,
            address: state.address,
            city: state.city,
            state: state.state,
            latitude: state.latitude,
            longitude: state.longitude,
            max_capacity: parseInt(state.max_capacity) || null
        };

        console.log('Submitting event:', eventData);

        // Make API call to the backend endpoint
        const response = await fetch(config.public.backendUrl + '/event/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${store.session}` // Use auth token from store
            },
            body: JSON.stringify(eventData)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to create event');
        }

        const createdEvent = await response.json();
        console.log('Event created:', createdEvent);

        // Save the created event ID and show the tier setup component for paid events
        state.createdEventId = createdEvent.id;
        state.showTierSetup = state.event_type === 'Paid';
        state.showFileUpload = state.event_type === 'Free';

        toast.add({
            title: 'Success',
            description: 'Event created successfully. Proceed to the next step.',
            color: 'success'
        });
    } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Failed to create event. Please try again.';
        state.error = errorMessage;
        toast.add({
            title: 'Event Creation Failed',
            description: state.error,
            color: 'error'
        });
    } finally {
        state.isLoading = false;
    }
};

const finishAndGoHome = () => {
    router.push('/');
};
</script>

<template>
    <UContainer class="py-8">
        <!-- Event Creation Form -->
        <UCard v-if="!state.showFileUpload && !state.showTierSetup" class="w-full max-w-3xl mx-auto">
            <template #header>
                <div class="flex flex-col gap-1">
                    <h2 class="text-xl font-semibold">Create New Event</h2>
                    <p class="text-sm text-gray-500">Fill in the details to create a new community event</p>
                </div>
            </template>

            <UForm :state="state" class="flex flex-col gap-6" @submit.prevent="createEvent">
                <!-- Basic Event Info -->
                <div class="space-y-4">
                    <h3 class="font-medium">Event Details</h3>
                    <UFormField label="Event Name" name="event_name" required>
                        <UInput v-model="state.event_name" type="text" placeholder="Enter event name" class="w-full"
                            required />
                    </UFormField>

                    <UFormField label="Event Description" name="event_description" required>
                        <UTextarea v-model="state.event_description" placeholder="Describe your event..." :rows="4"
                            class="w-full" required />
                    </UFormField>

                    <UFormField label="Category" name="category" required>
                        <USelect v-model="state.category" :items="categories" placeholder="Select event category"
                            class="w-full" required />
                    </UFormField>

                    <UFormField label="Event Type" name="event_type" required>
                        <USelect v-model="state.event_type" :items="['Free', 'Paid']" placeholder="Select event type"
                            class="w-full" required />
                    </UFormField>

                    <UFormField label="Max Capacity" name="max_capacity" required>
                        <UInput type="text" inputmode="numeric" placeholder="Maximum number of participants"
                            class="w-full" required :value="state.max_capacity"
                            @keypress="(e) => { if (!/[0-9]/.test(e.key)) e.preventDefault(); }"
                            @input="(e) => { state.max_capacity = e.target.value.replace(/[^0-9]/g, '') }" />
                    </UFormField>
                </div>

                <!-- Event Dates -->
                <div class="space-y-4">
                    <h3 class="font-medium">Event Schedule</h3>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <UFormField label="Start Date" name="start_date" required>
                            <UInput v-model="state.start_date" type="datetime-local" class="w-full" required />
                        </UFormField>

                        <UFormField label="End Date" name="end_date" required>
                            <UInput v-model="state.end_date" type="datetime-local" class="w-full" required />
                        </UFormField>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <UFormField label="Registration Start" name="registration_start" required>
                            <UInput v-model="state.registration_start" type="datetime-local" class="w-full" required />
                        </UFormField>

                        <UFormField label="Registration End" name="registration_end" required>
                            <UInput v-model="state.registration_end" type="datetime-local" class="w-full" required />
                        </UFormField>
                    </div>
                </div>

                <!-- Event Location -->
                <div class="space-y-4">
                    <h3 class="font-medium">Event Location</h3>
                    <UFormField label="Address" name="address" required>
                        <UInput v-model="state.address" type="text" placeholder="Street address" class="w-full"
                            required />
                    </UFormField>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <UFormField label="City" name="city" required>
                            <UInput v-model="state.city" type="text" placeholder="City" class="w-full" required />
                        </UFormField>

                        <UFormField label="State" name="state" required>
                            <UInput v-model="state.state" type="text" placeholder="State" class="w-full" required />
                        </UFormField>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <UFormField label="Latitude" name="latitude" required>
                            <UInput type="text" inputmode="decimal" placeholder="Latitude" class="w-full" required
                                :value="state.latitude"
                                @keypress="(e) => { if (!/[0-9.-]/.test(e.key) || (e.key === '.' && state.latitude.includes('.')) || (e.key === '-' && state.latitude !== '')) e.preventDefault(); }"
                                @input="(e) => { state.latitude = e.target.value.replace(/[^0-9.-]/g, ''); }" />
                        </UFormField>

                        <UFormField label="Longitude" name="longitude" required>
                            <UInput type="text" inputmode="decimal" placeholder="Longitude" class="w-full" required
                                :value="state.longitude"
                                @keypress="(e) => { if (!/[0-9.-]/.test(e.key) || (e.key === '.' && state.longitude.includes('.')) || (e.key === '-' && state.longitude !== '')) e.preventDefault(); }"
                                @input="(e) => { state.longitude = e.target.value.replace(/[^0-9.-]/g, ''); }" />
                        </UFormField>
                    </div>

                    <div class="flex justify-center mt-4">
                        <UButton label="Get Current Location" type="button" variant="solid" color="secondary" size="xl"
                            class="px-8" :loading="state.locationLoading" @click="getCurrentLocation" />
                    </div>
                </div>

                <div class="flex justify-center mt-4">
                    <UButton label="Create Event" type="submit" variant="solid" color="primary" size="xl" class="px-8"
                        :loading="state.isLoading" />
                </div>

                <p v-if="state.error" class="text-red-500 text-sm text-center">{{ state.error }}</p>
            </UForm>
        </UCard>

        <!-- Tier Setup Component -->
        <UCard v-if="state.showTierSetup" class="w-full max-w-3xl mx-auto">
            <template #header>
                <div class="flex flex-col gap-1">
                    <h2 class="text-xl font-semibold">Setup Pricing Tiers</h2>
                    <p class="text-sm text-gray-500">Define pricing tiers for your paid event</p>
                </div>
            </template>

            <div class="space-y-4">
                <div v-for="(tier, index) in tiers.items" :key="index" class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <UFormField :label="`Tier Name ${index + 1}`" :name="`tier_name_${index}`" required>
                        <UInput v-model="tier.tier_name" type="text" placeholder="Enter tier name" class="w-full"
                            required />
                    </UFormField>

                    <UFormField :label="`Price ${index + 1}`" :name="`tier_price_${index}`" required>
                        <UInput type="text" inputmode="decimal" placeholder="Enter price" class="w-full" required
                            :value="tier.price"
                            @keypress="(e) => { if (!/[0-9.]/.test(e.key) || (e.key === '.' && tier.price.toString().includes('.'))) e.preventDefault(); }"
                            @input="(e) => { tier.price = e.target.value.replace(/[^0-9.]/g, ''); }" />
                    </UFormField>

                    <UFormField :label="`Quantity ${index + 1}`" :name="`tier_quantity_${index}`" required>
                        <UInput type="text" inputmode="numeric" placeholder="Enter quantity" class="w-full" required
                            :value="tier.quantity" @keypress="(e) => { if (!/[0-9]/.test(e.key)) e.preventDefault(); }"
                            @input="(e) => { tier.quantity = e.target.value.replace(/[^0-9]/g, '') }" />
                    </UFormField>

                    <div class="flex justify-end mt-2">
                        <UButton label="Remove Tier" type="button" variant="outline" color="error" size="sm"
                            @click="removeTier(index)" />
                    </div>
                </div>

                <!-- Remaining capacity display -->
                <div class="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
                    <div class="flex justify-between">
                        <span class="font-medium">Total capacity:</span>
                        <span>{{ state.max_capacity }} attendees</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="font-medium">Used in tiers:</span>
                        <span>{{ parseInt(state.max_capacity) - remainingCapacity }} attendees</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="font-medium">Remaining capacity:</span>
                        <span :class="{ 'text-red-500': remainingCapacity < 0 }">
                            {{ remainingCapacity }} attendees
                        </span>
                    </div>
                </div>

                <div class="flex justify-center mt-4">
                    <UButton label="Add Tier" type="button" variant="solid" color="secondary" size="md"
                        @click="addTier" />
                </div>

                <p v-if="tiers.error" class="text-red-500 text-sm text-center">{{ tiers.error }}</p>
            </div>

            <div class="flex justify-center mt-6">
                <UButton label="Save Tiers" type="button" variant="solid" color="primary" size="xl" class="px-8"
                    :loading="tiers.isLoading" @click="saveTiers" />
            </div>
        </UCard>

        <!-- File Upload Component (shown after event creation) -->
        <div v-if="state.showFileUpload">
            <h2 class="text-2xl font-semibold text-center mb-4">Upload Event Images</h2>
            <p class="text-center text-gray-600 mb-6">Upload up to 5 images for your event</p>

            <!-- File upload component with dynamically created event ID -->
            <fileUpload :linksubset="`/event/${state.createdEventId}`" />

            <div class="flex justify-center mt-6">
                <UButton label="Finish & Go to Home" icon="i-lucide-home" color="primary" @click="finishAndGoHome" />
            </div>
        </div>
    </UContainer>
</template>