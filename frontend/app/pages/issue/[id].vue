<template>
    <div class="container mx-auto px-4 py-8">
        <template v-if="issue">
            <!-- Issue Details Section -->
            <div class="mt-8 grid grid-cols-1 md:grid-cols-3 gap-8">
                <!-- Left Column - Issue Details -->
                <div class="md:col-span-2">
                    <UCard class="overflow-hidden">
                        <!-- Image Carousel if multiple images are available -->
                        <div v-if="issueImages.length > 0" class="w-full aspect-video">
                            <UCarousel v-slot="{ item }" :items="issueImages" dots class="w-full aspect-video">
                                <img :src="item" :alt="issue.category" class="w-full h-full object-cover rounded-lg">
                            </UCarousel>
                        </div>
                        <div v-else class="w-full aspect-video bg-gray-200 flex items-center justify-center">
                            <UIcon name="i-lucide-image" class="w-16 h-16 text-gray-400" />
                        </div>

                        <div class="p-4">
                            <div class="flex flex-col md:flex-row justify-between gap-4 mb-4">
                                <div>
                                    <h1 class="text-2xl md:text-3xl font-bold mb-2">{{ issue.category }}</h1>
                                    <div class="flex items-center text-sm text-gray-500">
                                        <UIcon name="i-lucide-clock" class="mr-1" />
                                        <span>Reported {{ formatDate(issue.created_at) }}</span>
                                    </div>
                                </div>
                                <UBadge :color="getStatusColor(issue.status)" size="lg" class="self-start">
                                    {{ formatStatus(issue.status) }}
                                </UBadge>
                            </div>

                            <!-- Issue Description -->
                            <div class="mt-6">
                                <h2 class="text-xl font-semibold mb-2">Issue Description</h2>
                                <p class="text-gray-400 whitespace-pre-wrap">{{ issue.description }}</p>
                            </div>

                            <!-- Personal Notes -->
                            <div v-if="isOwner && issue.personal" class="mt-6">
                                <h2 class="text-xl font-semibold mb-2">Owner Username</h2>
                                <div class="bg-primary-50 p-4 rounded-lg border border-primary-100">
                                    <p class="text-gray-600 whitespace-pre-wrap">{{ issue.personal }}</p>
                                </div>
                            </div>

                            <!-- Actions -->
                            <div class="mt-8 flex flex-wrap gap-3">
                                <!-- Upvote Button -->
                                <UButton 
                                    :color="hasUpvoted ? 'primary' : 'gray'" 
                                    :variant="hasUpvoted ? 'solid' : 'outline'" 
                                    @click="toggleUpvote">
                                    <template #leading>
                                        <UIcon :name="hasUpvoted ? 'i-lucide-thumbs-up-filled' : 'i-lucide-thumbs-up'" />
                                    </template>
                                    Upvote ({{ upvoteCount }})
                                </UButton>
                                
                                <!-- Spam Button -->
                                <UButton 
                                    v-if="!isOwner" 
                                    color="amber" 
                                    variant="outline" 
                                    @click="showSpamModal = true">
                                    <template #leading>
                                        <UIcon name="i-lucide-flag" />
                                    </template>
                                    Report as Spam
                                </UButton>
                                <p v-if="!isOwner" class="text-xs text-gray-500 mt-1 ml-1">
                                    Multiple reports will hide this issue
                                </p>
                                
                                <!-- Edit/Delete Buttons for Owner -->
                                <div v-if="isOwner" class="flex gap-2">
                                    <UButton 
                                        color="primary" 
                                        variant="outline" 
                                        :to="`/issue/update/${issueId}`">
                                        <template #leading>
                                            <UIcon name="i-lucide-edit" />
                                        </template>
                                        Edit Issue
                                    </UButton>
                                    <UButton 
                                        color="red" 
                                        variant="outline" 
                                        @click="showDeleteModal = true">
                                        <template #leading>
                                            <UIcon name="i-lucide-trash-2" />
                                        </template>
                                        Delete
                                    </UButton>
                                </div>

                                <!-- Share Button -->
                                <UButton 
                                    color="gray" 
                                    variant="outline" 
                                    @click="shareIssue">
                                    <template #leading>
                                        <UIcon name="i-lucide-share-2" />
                                    </template>
                                    Share
                                </UButton>
                            </div>
                        </div>
                    </UCard>
                </div>

                <!-- Right Column - Issue Information -->
                <div class="md:col-span-1">
                    <UCard class="mb-6">
                        <div class="p-4">
                            <!-- Issue Details -->
                            <div class="flex flex-col gap-4 mb-6">
                                <!-- Reporter -->
                                <div class="flex items-start gap-3">
                                    <UIcon name="i-lucide-user" class="w-5 h-5 mt-1 text-primary flex-shrink-0" />
                                    <div>
                                        <h3 class="font-medium">Reported by</h3>
                                        <p class="text-sm text-gray-500">{{ issue.personal === '' ? 'Anonymous' : issue.personal }}</p>
                                    </div>
                                </div>
                                
                                <!-- Category -->
                                <div class="flex items-start gap-3">
                                    <UIcon name="i-lucide-tag" class="w-5 h-5 mt-1 text-primary flex-shrink-0" />
                                    <div>
                                        <h3 class="font-medium">Category</h3>
                                        <p class="text-sm text-gray-500">{{ issue.category }}</p>
                                    </div>
                                </div>
                                
                                <!-- Status -->
                                <div class="flex items-start gap-3">
                                    <UIcon name="i-lucide-activity" class="w-5 h-5 mt-1 text-primary flex-shrink-0" />
                                    <div>
                                        <h3 class="font-medium">Status</h3>
                                        <p class="text-sm text-gray-500">{{ formatStatus(issue.status) }}</p>
                                    </div>
                                </div>
                                
                                <!-- Upvotes -->
                                <div class="flex items-start gap-3">
                                    <UIcon name="i-lucide-thumbs-up" class="w-5 h-5 mt-1 text-primary flex-shrink-0" />
                                    <div>
                                        <h3 class="font-medium">Community Support</h3>
                                        <p class="text-sm text-gray-500">{{ upvoteCount }} upvotes</p>
                                    </div>
                                </div>
                            </div>

                            <!-- Map if location available -->
                            <div v-if="hasLocation">
                                <h3 class="font-medium mb-2">Location</h3>
                                <LMap 
                                    class="mt-2 rounded-2xl" 
                                    style="height: 350px" 
                                    :zoom="15" 
                                    :center="latLong"
                                    :use-global-leaflet="false">
                                    <LTileLayer 
                                        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                                        attribution="&amp;copy; <a href=&quot;https://www.openstreetmap.org/&quot;>OpenStreetMap</a> contributors"
                                        layer-type="base" name="OpenStreetMap" />
                                    <LMarker :lat-lng="latLong" />
                                </LMap>
                            </div>
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
            <h2 class="text-xl font-semibold mb-2">Issue Not Found</h2>
            <p class="mb-4 text-gray-500">The issue you're looking for doesn't exist or has been removed.</p>
            <UButton to="/issues" icon="i-lucide-list">Back to Issues</UButton>
        </UCard>

        <!-- Delete Confirmation Modal -->
        <UModal v-if="showDeleteModal" v-model="showDeleteModal" class="mt-4" :ui="{ container: 'body' }">
            <UCard class="w-full max-w-md">
                <template #header>
                    <div class="flex items-center">
                        <UIcon name="i-lucide-alert-triangle" class="w-5 h-5 mr-2 text-red-500" />
                        <h3 class="text-lg font-medium">Delete Issue</h3>
                    </div>
                </template>

                <div class="py-4">
                    <p class="text-gray-400 mb-4">
                        Are you sure you want to delete this issue report?
                    </p>
                    <p
                        class="text-sm text-gray-500 bg-amber-50 p-3 rounded-md border border-amber-200">
                        <UIcon 
                            name="i-lucide-alert-circle"
                            class="w-4 h-4 inline-block mr-1 text-amber-500" />
                        This action cannot be undone. All issue data will be permanently removed.
                    </p>
                </div>

                <template #footer>
                    <div class="flex justify-end gap-3">
                        <UButton color="gray" variant="ghost" @click="showDeleteModal = false">
                            Cancel
                        </UButton>
                        <UButton 
                            color="error" 
                            variant="solid" 
                            icon="i-lucide-trash-2"
                            :loading="isDeleting" 
                            @click="deleteIssue">
                            Delete Issue
                        </UButton>
                    </div>
                </template>
            </UCard>
        </UModal>

        <!-- Report Spam Modal -->
        <UModal v-if="showSpamModal" v-model="showSpamModal" class="mt-4" :ui="{ container: 'body' }">
            <UCard class="w-full max-w-md">
                <template #header>
                    <div class="flex items-center">
                        <UIcon name="i-lucide-flag" class="w-5 h-5 mr-2 text-amber-500" />
                        <h3 class="text-lg font-medium">Report as Spam</h3>
                    </div>
                </template>

                <div class="py-4">
                    <p class="text-gray-400 mb-4">
                        Are you sure you want to report this issue as spam?
                    </p>
                    <p
                        class="text-sm text-gray-500 bg-blue-50 p-3 rounded-md border border-blue-200">
                        <UIcon 
                            name="i-lucide-info"
                            class="w-4 h-4 inline-block mr-1 text-blue-500" />
                        If multiple users report this issue as spam, it may be hidden from public view.
                    </p>
                </div>

                <template #footer>
                    <div class="flex justify-end gap-3">
                        <UButton color="gray" variant="ghost" @click="showSpamModal = false">
                            Cancel
                        </UButton>
                        <UButton 
                            color="amber" 
                            variant="solid" 
                            icon="i-lucide-flag"
                            :loading="isReportingSpam" 
                            @click="reportAsSpam">
                            Report as Spam
                        </UButton>
                    </div>
                </template>
            </UCard>
        </UModal>
    </div>
</template>

<script setup>
import { useAuthStore } from '../../../stores/authStore';

const route = useRoute();
const issueId = route.params.id;
const toast = useToast();
const authStore = useAuthStore();
const config = useRuntimeConfig();

// Data
const issue = ref(null);
const loading = ref(true);
const isDeleting = ref(false);
const isReportingSpam = ref(false);
const showDeleteModal = ref(false);
const showSpamModal = ref(false);
const upvoteCount = ref(0);
const hasUpvoted = ref(false);
const latLong = ref([0, 0]);
const issueImages = ref([]);

// Computed properties
const isOwner = computed(() =>
    authStore.user && issue.value && (authStore.user.isAdmin || authStore.user.username === issue.value.personal)
);

const hasLocation = computed(() => {
    return issue.value && issue.value.latitude && issue.value.longitude;
});

// Fetch issue details
const fetchIssueDetails = async () => {
    loading.value = true;
    try {
        const response = await fetch(`${config.public.backendUrl}/issue/${issueId}`);
        if (!response.ok) {
            throw new Error('Failed to fetch issue details');
        }

        const data = await response.json();
        console.log("Issue data:", data);
        
        // Check if the response has both issue data and images
        if (data.issue) {
            // New response format with issue and images
            issue.value = data.issue;
            
            // Process images if available
            if (data.images && Array.isArray(data.images) && data.images.length > 0) {
                console.log("Raw image data:", data.images);
                // Create image URLs based on backend URL pattern
                issueImages.value = data.images.map(imageName => {
                    // Check if imageName is already a full URL
                    if (imageName.startsWith('http')) {
                        return imageName;
                    }
                    return `${config.public.backendUrl}/uploads/${imageName}`;
                });
                console.log("Image URLs created:", issueImages.value);
            } else {
                // If there are no images provided, use a placeholder
                issueImages.value = ['https://placehold.co/800x450/EEE/31343C?text=No+Images+Available'];
            }
        } else {
            // Old response format without separate images
            issue.value = data;
            
            // Try to extract image from issue data if available
            if (data.image) {
                issueImages.value = [`${config.public.backendUrl}/uploads/${data.image}`];
            } else {
                // No images available, use placeholder
                issueImages.value = ['https://placehold.co/800x450/EEE/31343C?text=No+Images+Available'];
            }
        }
        
        // Set location coordinates if available
        if (issue.value.latitude && issue.value.longitude) {
            latLong.value = [
                parseFloat(issue.value.latitude),
                parseFloat(issue.value.longitude)
            ];
        }
        
        // Fetch upvotes count
        await fetchUpvotes();
        
        // Check if user has upvoted
        if (authStore.session) {
            await checkUserUpvoteStatus();
        }
    } catch (error) {
        console.error('Error fetching issue:', error);
        toast.add({
            title: 'Error',
            description: 'Failed to load issue details',
            color: 'error'
        });
    } finally {
        loading.value = false;
    }
};

// Format date
const formatDate = (dateStr) => {
    if (!dateStr) return 'Unknown';
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
};

// Format issue status
const formatStatus = (status) => {
    if (!status) return 'Unknown';
    
    switch (status.toLowerCase()) {
        case 'open':
            return 'Open';
        case 'in_progress':
            return 'In Progress';
        case 'resolved':
            return 'Resolved';
        case 'closed':
            return 'Closed';
        default:
            return status.charAt(0).toUpperCase() + status.slice(1);
    }
};

// Get color based on status
const getStatusColor = (status) => {
    if (!status) return 'gray';
    
    switch (status.toLowerCase()) {
        case 'open':
            return 'amber';
        case 'in_progress':
            return 'blue';
        case 'resolved':
            return 'green';
        case 'closed':
            return 'gray';
        default:
            return 'gray';
    }
};

// Fetch upvotes count
const fetchUpvotes = async () => {
    try {
        const response = await fetch(`${config.public.backendUrl}/issues/${issueId}/upvotes`);
        if (response.ok) {
            upvoteCount.value = await response.json();
        }
    } catch (error) {
        console.error('Error fetching upvotes:', error);
    }
};

// Check if user has upvoted this issue
const checkUserUpvoteStatus = async () => {
    // This endpoint is not in the OpenAPI spec, so assuming a similar structure as event upvotes
    // The backend would need to implement this endpoint
    try {
        const token = authStore.session;
        if (!token) return;
        
        const response = await fetch(`${config.public.backendUrl}/issues/${issueId}/has-upvoted`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            hasUpvoted.value = data.upvoted;
        }
    } catch (error) {
        console.error('Error checking user upvote status:', error);
        // Assume not upvoted in case of error
        hasUpvoted.value = false;
    }
};

// Toggle upvote for an issue
const toggleUpvote = async () => {
    if (!authStore.session) {
        toast.add({
            title: 'Authentication Required',
            description: 'Please log in to upvote issues',
            color: 'amber'
        });
        navigateTo('/login');

    }

    try {
        const response = await fetch(`${config.public.backendUrl}/issues/${issueId}/upvote`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authStore.session}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) throw new Error('Failed to upvote');

        // Toggle upvote state locally and update count
        if (!hasUpvoted.value) {
            upvoteCount.value++;
            hasUpvoted.value = true;
            toast.add({
                title: 'Upvoted',
                description: 'You have upvoted this issue',
                color: 'green'
            });
        } else {
            // This would require a separate API endpoint to remove an upvote
            // For now, we'll just assume upvotes are permanent
            toast.add({
                title: 'Already Upvoted',
                description: 'You have already upvoted this issue',
                color: 'blue'
            });
        }
    } catch (error) {
        toast.add({
            title: 'Error',
            description: error.message || 'Failed to upvote issue',
            color: 'error'
        });
    }
};

// Delete issue
const deleteIssue = async () => {
    isDeleting.value = true;
    try {
        const response = await fetch(`${config.public.backendUrl}/issues/delete/${issueId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${authStore.session}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error('Failed to delete issue');
        }

        // Close the modal first
        showDeleteModal.value = false;

        // Small delay to ensure modal is fully closed before showing toast
        await new Promise(resolve => setTimeout(resolve, 100));

        toast.add({
            title: 'Success',
            description: 'Issue deleted successfully',
            color: 'green'
        });

        // Redirect to issues list
        navigateTo('/issues');
    } catch (error) {
        console.error('Error deleting issue:', error);
        toast.add({
            title: 'Error',
            description: error.message || 'Failed to delete issue',
            color: 'error'
        });
    } finally {
        isDeleting.value = false;
    }
};

// Report issue as spam
const reportAsSpam = async () => {
    if (!authStore.session) {
        toast.add({
            title: 'Authentication Required',
            description: 'Please log in to report issues',
            color: 'amber'
        });
        return;
    }

    isReportingSpam.value = true;
    try {
        const response = await fetch(`${config.public.backendUrl}/issues/${issueId}/spam`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authStore.session}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error('Failed to report issue as spam');
        }

        // Close the modal
        showSpamModal.value = false;

        // Small delay
        await new Promise(resolve => setTimeout(resolve, 100));

        toast.add({
            title: 'Reported',
            description: 'You have reported this issue as spam',
            color: 'green'
        });
    } catch (error) {
        console.error('Error reporting issue as spam:', error);
        toast.add({
            title: 'Error',
            description: error.message || 'Failed to report issue',
            color: 'error'
        });
    } finally {
        isReportingSpam.value = false;
    }
};

// Share issue
const shareIssue = async () => {
    if (navigator.share) {
        try {
            await navigator.share({
                title: `Community Issue: ${issue.value.category}`,
                text: `Check out this community issue: ${issue.value.description?.substring(0, 100)}...`,
                url: window.location.href
            });
        } catch (error) {
            if (error.name !== 'AbortError') {
                toast.add({
                    title: 'Sharing Failed',
                    description: 'Could not share this issue',
                    color: 'amber'
                });
            }
        }
    } else {
        // Fallback - copy link to clipboard
        navigator.clipboard.writeText(window.location.href);
        toast.add({
            title: 'Link Copied',
            description: 'Issue link copied to clipboard',
            color: 'green'
        });
    }
};

// Fetch data on page load
onMounted(() => {
    fetchIssueDetails();
});
</script>