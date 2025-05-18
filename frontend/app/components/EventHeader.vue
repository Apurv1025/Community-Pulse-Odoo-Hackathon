<template>
  <div class="image-header" :style="headerStyle">
    <div class="header-overlay" :style="overlayStyle">
      <div class="header-content">
        <h1 class="header-title">{{ event_id }}</h1>
        <slot></slot>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
event_id:{
    type:String
}})

</script>

<style scoped>

</style>
