<script setup lang="ts">
import { useAuthStore } from "../../../stores/authStore";

const store = useAuthStore();
const router = useRouter();
const config = useRuntimeConfig();
const toast = useToast();

const state = reactive({
    category: '',
    description: '',
    latitude: '',
    longitude: '',
    personal: store.user?.username || '', // Default to the user's username
    isAnonymous: false, // New toggle for anonymous submission
    error: '',
    isLoading: false,
    locationLoading: false,
    showFileUpload: false, // Control to show file upload component
    createdIssueId: null, // To store the ID of the newly created issue
});

// Default categories list
const categories = ref([
    'Infrastructure',
    'Sanitation',
    'Public Safety',
    'Environment',
    'Noise Pollution',
    'Public Services',
    'Traffic',
    'Other'
]);

// Watch for changes to the isAnonymous toggle and update the personal field accordingly
watch(() => state.isAnonymous, (newValue) => {
    state.personal = newValue ? '' : (store.user?.username || '');
});

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

const finishAndGoHome = () => {
    router.push('/');
};

const createIssue = async () => {
    state.isLoading = true;
    state.error = '';

    // Validate required fields
    if (!state.category) {
        state.error = 'Category is required';
        state.isLoading = false;
        toast.add({
            title: 'Validation Error',
            description: state.error,
            color: 'error'
        });
        return;
    }

    if (!state.description) {
        state.error = 'Description is required';
        state.isLoading = false;
        toast.add({
            title: 'Validation Error',
            description: state.error,
            color: 'error'
        });
        return;
    }
    
    // Validate location fields
    if (!state.latitude || !state.longitude) {
        state.error = 'Location is required. Please use the "Get Current Location" button or enter coordinates manually.';
        state.isLoading = false;
        toast.add({
            title: 'Validation Error',
            description: state.error,
            color: 'error'
        });
        return;
    }

    // For anonymous submissions, this is fine
    // For non-anonymous submissions, the personal field will contain the username

    try {
        // Create an issue object matching the backend IssueCreate model
        const issueData = {
            category: state.category,
            description: state.description,
            latitude: state.latitude ? parseFloat(state.latitude) : null,
            longitude: state.longitude ? parseFloat(state.longitude) : null,
            personal: state.personal
        };

        console.log('Submitting issue:', issueData);

        // Make API call to the backend endpoint
        const response = await fetch(config.public.backendUrl + '/issues/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${store.session}` // Use auth token from store
            },
            body: JSON.stringify(issueData)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to create issue');
        }

        const createdIssue = await response.json();
        console.log('Issue created:', createdIssue);
        
        // Save the created issue ID and show file upload component
        state.createdIssueId = createdIssue.id;
        state.showFileUpload = true;

        toast.add({
            title: 'Success',
            description: 'Issue reported successfully. You can now upload images for this issue.',
            color: 'success'
        });
    } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Failed to report issue. Please try again.';
        state.error = errorMessage;
        toast.add({
            title: 'Issue Reporting Failed',
            description: state.error,
            color: 'error'
        });
    } finally {
        state.isLoading = false;
    }
};
</script>

<template>
    <UContainer class="py-8">
        <!-- Issue Creation Form -->
        <UCard v-if="!state.showFileUpload" class="w-full max-w-3xl mx-auto">
            <template #header>
                <div class="flex flex-col gap-1">
                    <h2 class="text-xl font-semibold">Report Community Issue</h2>
                    <p class="text-sm text-gray-500">Fill in the details to report an issue in your community</p>
                </div>
            </template>

            <UForm :state="state" class="flex flex-col gap-6" @submit.prevent="createIssue">
                <!-- Issue Details -->
                <div class="space-y-4">
                    <h3 class="font-medium">Issue Details</h3>
                    <UFormField label="Category" name="category" required>
                        <USelect 
                            v-model="state.category" 
                            :items="categories" 
                            placeholder="Select issue category"
                            class="w-full" 
                            required />
                    </UFormField>

                    <UFormField label="Description" name="description" required>
                        <UTextarea 
                            v-model="state.description" 
                            placeholder="Describe the issue in detail..." 
                            :rows="4"
                            class="w-full" 
                            required />
                    </UFormField>

                    <UFormField name="isAnonymous">
                        <template #label>
                            <div class="flex items-center">
                                <span class="mr-2">Submit Anonymously</span>
                            </div>
                        </template>
                        <UCheckbox 
                            v-model="state.isAnonymous" 
                            label="Submit this issue anonymously" 
                            name="anonymous" />
                        <div class="text-sm text-gray-500 mt-2">
                            <strong>{{ state.isAnonymous ? 'Anonymous: ' : 'Not Anonymous: ' }}</strong>
                            {{ state.isAnonymous ? 'Your username will not be associated with this issue' : 'Your username will be associated with this issue' }}
                        </div>
                        <div v-if="state.isAnonymous" class="mt-2 text-sm text-amber-600 bg-amber-400 p-2 rounded border border-amber-200">
                            <strong>Warning:</strong> When submitting anonymously, you will not be able to edit the issue status later.
                        </div>
                    </UFormField>
                </div>

                <!-- Issue Location -->
                <div class="space-y-4">
                    <h3 class="font-medium">Issue Location</h3>
                    <p class="text-sm text-gray-500">Location is required to help others identify where this issue is occurring</p>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <UFormField label="Latitude" name="latitude">
                            <UInput 
                                type="text" 
                                inputmode="decimal" 
                                placeholder="Latitude" 
                                class="w-full"
                                :value="state.latitude"
                                @keypress="(e: KeyboardEvent) => { if (!/[0-9.-]/.test(e.key) || (e.key === '.' && state.latitude.includes('.')) || (e.key === '-' && state.latitude !== '')) e.preventDefault(); }"
                                @input="(e: Event) => { state.latitude = (e.target as HTMLInputElement).value.replace(/[^0-9.-]/g, ''); }" />
                        </UFormField>

                        <UFormField label="Longitude" name="longitude">
                            <UInput 
                                type="text" 
                                inputmode="decimal" 
                                placeholder="Longitude" 
                                class="w-full"
                                :value="state.longitude"
                                @keypress="(e: KeyboardEvent) => { if (!/[0-9.-]/.test(e.key) || (e.key === '.' && state.longitude.includes('.')) || (e.key === '-' && state.longitude !== '')) e.preventDefault(); }"
                                @input="(e: Event) => { state.longitude = (e.target as HTMLInputElement).value.replace(/[^0-9.-]/g, ''); }" />
                        </UFormField>
                    </div>

                    <div class="flex justify-center mt-4">
                        <UButton 
                            label="Get Current Location" 
                            type="button" 
                            variant="solid" 
                            color="secondary" 
                            size="xl"
                            class="px-8" 
                            :loading="state.locationLoading" 
                            @click="getCurrentLocation" />
                    </div>
                </div>

                <div class="flex justify-center mt-4">
                    <UButton 
                        label="Report Issue" 
                        type="submit" 
                        variant="solid" 
                        color="primary" 
                        size="xl" 
                        class="px-8"
                        :loading="state.isLoading" />
                </div>

                <p 
                    v-if="state.error" 
                    class="text-red-500 text-sm text-center">{{ state.error }}</p>
            </UForm>
        </UCard>

        <!-- File Upload Component (shown after issue creation) -->
        <div v-if="state.showFileUpload">
            <h2 class="text-2xl font-semibold text-center mb-4">Upload Issue Images</h2>
            <p class="text-center text-gray-600 mb-6">Upload up to 5 images for your issue</p>

            <!-- File upload component with dynamically created issue ID -->
            <fileUpload :linksubset="`/issue/${state.createdIssueId}`" />

            <div class="flex justify-center mt-6">
                <UButton 
                    label="Finish & Go to Home" 
                    icon="i-lucide-list" 
                    color="primary" 
                    @click="finishAndGoHome" />
            </div>
        </div>
    </UContainer>
</template>