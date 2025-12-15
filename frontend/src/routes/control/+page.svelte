<script lang="ts">
	import { createVehiclesQuery } from '$lib/api/queries';

	const vehiclesQuery = createVehiclesQuery();
</script>

<div class="space-y-6">
	<div>
		<h1 class="text-3xl font-bold">Vehicle Control</h1>
		<p class="text-muted-foreground">Control charging, preconditioning, and more</p>
	</div>

	{#if $vehiclesQuery.isLoading}
		<div class="rounded-lg border bg-card p-8 text-center">
			<p class="text-muted-foreground">Loading vehicles...</p>
		</div>
	{:else if $vehiclesQuery.isError}
		<div class="rounded-lg border border-destructive bg-destructive/10 p-4">
			<p class="text-sm text-destructive">
				Error loading vehicles: {$vehiclesQuery.error?.message}
			</p>
		</div>
	{:else if $vehiclesQuery.data}
		<div class="rounded-lg border bg-card">
			<div class="border-b p-4">
				<h2 class="text-lg font-semibold">Vehicle Controls</h2>
			</div>
			<div class="p-4">
				<p class="text-sm text-muted-foreground">
					Vehicle control panel will be implemented here (charge, preconditioning, horn, lights, locks)
				</p>
			</div>
		</div>
	{/if}
</div>
