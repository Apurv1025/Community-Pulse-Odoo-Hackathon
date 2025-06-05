<template>
    <UCard class="relative">
        <!-- Flag button -->
        <div class="absolute top-2 right-2 z-10 ml-auto self-end" style="right: 8px; top: 8px; position: absolute;">
            <UButton color="error" variant="ghost" icon="i-lucide-flag" size="sm" :loading="event.flagging"
                :disabled="event.processing" @click="onFlag(event.id)" />
        </div>

        <!-- Card content -->
        <h3 class="text-lg font-semibold mb-1">{{ event.event_name }}</h3>

        <div class="flex gap-4 mb-4">
            <!-- Event Details -->
            <div class="flex-1 text-sm text-gray-500">
                <div class="flex items-center gap-1 mb-1">
                    <UIcon name="i-lucide-calendar" class="w-4 h-4" />
                    <span>{{ formatDate(event.start_date) }}</span>
                </div>
                <div class="flex items-center gap-1 mb-1">
                    <UIcon name="i-lucide-map-pin" class="w-4 h-4" />
                    <span>{{ event.city }}, {{ event.state }}</span>
                </div>
                <div class="flex items-center gap-1 mb-1">
                    <UIcon name="i-lucide-tag" class="w-4 h-4" />
                    <span>{{ event.category }}</span>
                </div>
                <div class="flex items-center gap-1">
                    <UIcon name="i-lucide-user" class="w-4 h-4" />
                    <span>{{ event.organiser }}</span>
                </div>
            </div>

            <!-- Square Image -->
            <div v-if="event.image" class="w-24 h-24 flex-shrink-0 overflow-hidden"
                style="min-width: 96px; min-height: 96px; max-width: 96px; max-height: 96px; flex: 0 0 96px; display: block;">
                <img :src="event.image_url" :alt="event.event_name" class="w-full h-full object-cover rounded-md"
                    style="object-fit: cover; width: 100%; height: 100%;">
            </div>
            <div v-else class="w-24 h-24 flex-shrink-0 overflow-hidden bg-gray-100 flex items-center justify-center"
                style="min-width: 96px; min-height: 96px; max-width: 96px; max-height: 96px; flex: 0 0 96px; display: block;">
                <UIcon name="i-lucide-image" class="w-10 h-10 text-gray-300" />
            </div>
        </div>

        <p class="text-gray-700 mb-4 line-clamp-3">{{ event.event_description }}</p>

        <div class="flex flex-col sm:flex-row gap-2 mt-auto">
            <UButton color="success" variant="solid" block icon="i-lucide-check" size="md"
                :loading="event.processing && event.actionType === 'approve'" :disabled="event.processing"
                @click="onApprove(event.id)">
                Approve
            </UButton>
            <UButton color="error" variant="outline" block icon="i-lucide-x" size="md"
                :loading="event.processing && event.actionType === 'reject'" :disabled="event.processing"
                @click="onReject(event.id)">
                Reject
            </UButton>
        </div>
    </UCard>
</template>

<script setup>
defineProps({
    event: {
        type: Object,
        required: true
    },
    imageUrl: {
        type: String,
        default: ''
    }
});

const emit = defineEmits(['approve', 'reject', 'flag']);

// Pass events up to parent component
const onApprove = (eventId) => {
    emit('approve', eventId);
};

const onReject = (eventId) => {
    emit('reject', eventId);
};

const onFlag = (eventId) => {
    emit('flag', eventId);
};

// Format date for display
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
</script>