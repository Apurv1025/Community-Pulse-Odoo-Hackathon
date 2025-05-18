<template>
    <EventHeader :event_id="eventId" />
</template>


<script setup>
const route = useRoute();
const eventId = route.params.id;
</script>