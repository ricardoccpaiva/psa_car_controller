<script lang="ts">
	import { createSettingsQuery } from '$lib/api/queries';

	const settingsQuery = createSettingsQuery();
</script>

<div class="space-y-6">
	<div>
		<h1 class="text-3xl font-bold">Settings</h1>
		<p class="text-muted-foreground">Configure your PSA Car Controller</p>
	</div>

	{#if $settingsQuery.isLoading}
		<div class="rounded-lg border bg-card p-8 text-center">
			<p class="text-muted-foreground">Loading settings...</p>
		</div>
	{:else if $settingsQuery.isError}
		<div class="rounded-lg border border-destructive bg-destructive/10 p-4">
			<p class="text-sm text-destructive">
				Error loading settings: {$settingsQuery.error?.message}
			</p>
		</div>
	{:else if $settingsQuery.data}
		<div class="rounded-lg border bg-card">
			<div class="border-b p-4">
				<h2 class="text-lg font-semibold">Configuration</h2>
			</div>
			<div class="p-4">
				<p class="text-sm text-muted-foreground">
					Settings panel will be implemented here (OAuth, ABRP, general settings)
				</p>
			</div>
		</div>
	{/if}
</div>
