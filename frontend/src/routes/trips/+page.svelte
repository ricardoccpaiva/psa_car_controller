<script lang="ts">
	import { createTripsQuery } from '$lib/api/queries';

	const tripsQuery = createTripsQuery();
</script>

<div class="space-y-6">
	<div>
		<h1 class="text-3xl font-bold">Trips</h1>
		<p class="text-muted-foreground">View and analyze your trip history</p>
	</div>

	{#if $tripsQuery.isLoading}
		<div class="rounded-lg border bg-card p-8 text-center">
			<p class="text-muted-foreground">Loading trips...</p>
		</div>
	{:else if $tripsQuery.isError}
		<div class="rounded-lg border border-destructive bg-destructive/10 p-4">
			<p class="text-sm text-destructive">
				Error loading trips: {$tripsQuery.error?.message}
			</p>
		</div>
	{:else if $tripsQuery.data}
		<div class="rounded-lg border bg-card">
			<div class="border-b p-4">
				<h2 class="text-lg font-semibold">Trip History ({$tripsQuery.data.length} trips)</h2>
			</div>
			<div class="p-4">
				<p class="text-sm text-muted-foreground">
					Trips table and charts will be implemented here
				</p>
			</div>
		</div>
	{/if}
</div>
