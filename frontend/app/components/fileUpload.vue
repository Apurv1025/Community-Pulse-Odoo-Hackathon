<script setup lang="ts">
import { useAuthStore } from "../../stores/authStore"
import { ref, reactive } from 'vue'

// Define props with a string parameter from parent
const props = defineProps<{
    linksubset?: string
}>()

const runtimeConfig = useRuntimeConfig()
const authStore = useAuthStore()
const toast = useToast()

const fileInput = ref<HTMLInputElement | null>(null)
const imagePreview = ref<string[] | null>(null)

const state = reactive({
    isLoading: false,
    uploadError: '',
    uploadSuccess: false,
    selectedFiles: [] as File[],
    currentUploadIndex: 0,
    uploadProgress: 0,
    totalUploaded: 0
})

const handleFileChange = (event: Event) => {
    const target = event.target as HTMLInputElement
    if (target.files && target.files.length > 0) {
        // Enforce 5 image limit
        if (target.files.length > 5) {
            state.uploadError = 'You can only upload a maximum of 5 images at once'
            toast.add({
                title: 'Selection Limit',
                description: state.uploadError,
                color: 'warning'
            })
            // Take only the first 5 files if more are selected
            state.selectedFiles = Array.from(target.files).slice(0, 5)
        } else {
            state.selectedFiles = Array.from(target.files)
        }

        // Create previews for images
        const previews: string[] = []
        state.selectedFiles.forEach(file => {
            const reader = new FileReader()
            reader.onload = (e) => {
                if (e.target?.result) {
                    previews.push(e.target.result as string)
                    if (previews.length === state.selectedFiles.length) {
                        imagePreview.value = previews
                    }
                }
            }
            reader.readAsDataURL(file)
        })

        // Reset any previous errors/success
        state.uploadError = ''
        state.uploadSuccess = false
        state.currentUploadIndex = 0
        state.uploadProgress = 0
        state.totalUploaded = 0
    }
}

const triggerFileInput = () => {
    if (fileInput.value) {
        fileInput.value.click()
    }
}

const uploadFile = async () => {
    if (state.selectedFiles.length === 0) {
        state.uploadError = 'Please select at least one file first'
        toast.add({
            title: 'Error',
            description: state.uploadError,
            color: 'error'
        })
        return
    }

    state.isLoading = true
    state.uploadError = ''
    state.currentUploadIndex = 0
    state.totalUploaded = 0

    await uploadNextFile()
}

const uploadNextFile = async () => {
    if (state.currentUploadIndex >= state.selectedFiles.length) {
        state.isLoading = false
        state.uploadSuccess = true
        toast.add({
            title: 'Success',
            description: `All ${state.totalUploaded} files uploaded successfully`,
            color: 'success'
        })
        return
    }

    const currentFile = state.selectedFiles[state.currentUploadIndex]

    try {
        const formData = new FormData()
        formData.append('file', currentFile)

        const response = await fetch(`${runtimeConfig.public.backendUrl}${props.linksubset}/upload`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authStore.session}`
            },
            body: formData
        })

        if (!response.ok) {
            throw new Error(`Upload failed with status: ${response.status}`)
        }

        const result = await response.json()
        state.totalUploaded++
        state.uploadProgress = Math.round((state.totalUploaded / state.selectedFiles.length) * 100)

        toast.add({
            title: 'Success',
            description: `File "${result.filename}" uploaded successfully (${state.totalUploaded}/${state.selectedFiles.length})`,
            color: 'success'
        })

        // Move to next file
        state.currentUploadIndex++
        await uploadNextFile()

    } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Upload failed. Please try again.'
        state.uploadError = `Error uploading file ${state.currentUploadIndex + 1}: ${errorMessage}`
        toast.add({
            title: 'Upload failed',
            description: state.uploadError,
            color: 'error'
        })
        state.isLoading = false
    }
}

const clearSelection = () => {
    state.selectedFiles = []
    imagePreview.value = null
    if (fileInput.value) fileInput.value.value = ''
    state.uploadError = ''
    state.uploadSuccess = false
    state.uploadProgress = 0
    state.totalUploaded = 0
}
</script>

<template>
    <UCard class="w-full max-w-lg mx-auto">
        <template #header>
            <div class="flex items-center justify-between">
                <h2 class="text-xl font-semibold">File Upload</h2>
                <UIcon name="i-lucide-upload" class="text-primary text-xl" />
            </div>
        </template>

        <div class="flex flex-col gap-4">
            <p class="text-muted mb-2">Select image files to upload to the server.</p>

            <div class="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center cursor-pointer hover:bg-gray-50 transition-colors"
                @click="triggerFileInput">
                <input ref="fileInput" type="file" class="hidden" accept="image/*" multiple @change="handleFileChange">

                <div v-if="!imagePreview || imagePreview.length === 0"
                    class="flex flex-col items-center justify-center gap-2">
                    <UIcon name="i-lucide-image-plus" class="text-4xl text-gray-400" />
                    <p class="text-gray-500">Click to select image files (maximum 5)</p>
                    <p class="text-xs text-gray-400 mt-1">Supported formats: JPG, PNG, GIF</p>
                </div>

                <div v-else class="flex flex-col items-center gap-2">
                    <div class="grid grid-cols-3 gap-2">
                        <div v-for="(preview, index) in imagePreview" :key="index" class="relative">
                            <img :src="preview" alt="Preview" class="h-24 w-24 object-cover rounded">
                        </div>
                    </div>
                    <p class="text-sm text-gray-600 mt-2">Selected {{ state.selectedFiles.length }} files</p>
                    <p class="text-xs text-gray-400">
                        {{Math.round(state.selectedFiles.reduce((acc, file) => acc + file.size, 0) / 1024)}} KB total
                    </p>
                </div>
            </div>

            <div v-if="state.uploadProgress > 0 && state.uploadProgress < 100"
                class="w-full bg-gray-200 rounded-full h-2.5">
                <div class="bg-primary h-2.5 rounded-full" :style="{ width: `${state.uploadProgress}%` }"></div>
                <p class="text-xs text-gray-500 text-center mt-1">
                    Uploading: {{ state.totalUploaded }}/{{ state.selectedFiles.length }} files ({{ state.uploadProgress
                    }}%)
                </p>
            </div>

            <div v-if="state.selectedFiles.length > 0" class="flex gap-2 justify-end mt-2">
                <UButton color="neutral" variant="soft" icon="i-lucide-x" label="Clear" @click="clearSelection" />
                <UButton color="primary" :loading="state.isLoading" icon="i-lucide-upload"
                    :label="`Upload ${state.selectedFiles.length} ${state.selectedFiles.length === 1 ? 'File' : 'Files'}`"
                    @click="uploadFile" />
            </div>

            <UButton v-else color="neutral" variant="soft" class="self-center" icon="i-lucide-plus" label="Select Files"
                @click="triggerFileInput" />

            <p v-if="state.uploadError" class="text-red-500 text-sm text-center">{{ state.uploadError }}</p>
            <p v-if="state.uploadSuccess" class="text-green-500 text-sm text-center">
                All files uploaded successfully!
            </p>
        </div>
    </UCard>
</template>