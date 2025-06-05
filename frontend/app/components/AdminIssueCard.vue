<template>
    <UCard class="relative">
        <!-- Flag button -->
        <div class="absolute top-2 right-2 z-10 ml-auto self-end" style="right: 8px; top: 8px; position: absolute;">
            <UButton 
                color="error" 
                variant="ghost" 
                icon="i-lucide-flag" 
                size="sm" 
                :loading="issue.flagging"
                :disabled="issue.processing" 
                @click="onFlag(issue.id)" />
        </div>

        <!-- Card content -->
        <h3 class="text-lg font-semibold mb-1">{{ issue.category }}</h3>

        <div class="flex gap-4 mb-4">
            <!-- Issue Details -->
            <div class="flex-1 text-sm text-gray-500">
                <div class="flex items-center gap-1 mb-1">
                    <UIcon name="i-lucide-calendar" class="w-4 h-4" />
                    <span>{{ formatDate(issue.created_at) }}</span>
                </div>
                <div class="flex items-center gap-1 mb-1">
                    <UIcon name="i-lucide-map-pin" class="w-4 h-4" />
                    <span>{{ formatLocation(issue.latitude, issue.longitude) }}</span>
                </div>
                <div class="flex items-center gap-1 mb-1">
                    <UIcon name="i-lucide-tag" class="w-4 h-4" />
                    <span>{{ issue.category }}</span>
                </div>
                <div class="flex items-center gap-1">
                    <UIcon name="i-lucide-user" class="w-4 h-4" />
                    <span>{{ issue.personal || 'Anonymous' }}</span>
                </div>
            </div>

            <!-- Square Image -->
            <div 
                v-if="issue.image" 
                class="w-24 h-24 flex-shrink-0 overflow-hidden"
                style="min-width: 96px; min-height: 96px; max-width: 96px; max-height: 96px; flex: 0 0 96px; display: block;">
                <img 
                    :src="issue.image_url" 
                    :alt="issue.category" 
                    class="w-full h-full object-cover rounded-md"
                    style="object-fit: cover; width: 100%; height: 100%;">
            </div>
            <div 
                v-else 
                class="w-24 h-24 flex-shrink-0 overflow-hidden bg-gray-100 flex items-center justify-center"
                style="min-width: 96px; min-height: 96px; max-width: 96px; max-height: 96px; flex: 0 0 96px; display: block;">
                <UIcon name="i-lucide-alert-triangle" class="w-10 h-10 text-gray-300" />
            </div>
        </div>

        <p class="text-gray-700 mb-4 line-clamp-3">{{ issue.description }}</p>

        <div class="flex items-center justify-between mb-3">
            <UBadge :color="getStatusColor(issue.status)" class="mr-2">
                {{ formatStatus(issue.status) }}
            </UBadge>
            <div class="text-sm text-gray-500">
                <UIcon name="i-lucide-thumbs-up" class="w-4 h-4 inline-block" /> {{ issue.upvotes || 0 }} upvotes
            </div>
        </div>

        <div class="flex justify-center mt-auto">
            <UButton 
                color="success" 
                variant="solid" 
                icon="i-lucide-eye" 
                size="md"
                :loading="issue.processing" 
                :disabled="issue.processing"
                @click="onUnhide(issue.id)">
                Unhide Issue
            </UButton>
        </div>
    </UCard>
</template>

<script setup>
defineProps({
    issue: {
        type: Object,
        required: true
    },
    imageUrl: {
        type: String,
        default: ''
    }
});

const emit = defineEmits(['unhide', 'flag']);

// Pass events up to parent component
const onUnhide = (issueId) => {
    emit('unhide', issueId);
};

const onFlag = (issueId) => {
    emit('flag', issueId);
};

// Format date for display
const formatDate = (dateStr) => {
    if (!dateStr) return 'TBD';
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
};

// Format location for display
const formatLocation = (lat, lng) => {
    if (!lat || !lng) return 'Location unavailable';
    return `${parseFloat(lat).toFixed(4)}, ${parseFloat(lng).toFixed(4)}`;
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
</script>