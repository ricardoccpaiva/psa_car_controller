<script lang="ts">
	import { createChargingsQuery } from '$lib/api/queries';

	const chargingsQuery = createChargingsQuery();
</script>

<div class="space-y-6">
	<div>
		<h1 class="text-3xl font-bold">Charging</h1>
		<p class="text-muted-foreground">View charging history and statistics</p>
	</div>

	{#if $chargingsQuery.isLoading}
		<div class="rounded-lg border bg-card p-8 text-center">
			<p class="text-muted-foreground">Loading charging sessions...</p>
		</div>
	{:else if $chargingsQuery.isError}
		<div class="rounded-lg border border-destructive bg-destructive/10 p-4">
			<p class="text-sm text-destructive">
				Error loading charging data: {$chargingsQuery.error?.message}
			</p>
		</div>
	{:else if $chargingsQuery.data}
		<div class="rounded-lg border bg-card">
			<div class="border-b p-4">
				<h2 class="text-lg font-semibold">
					Charging Sessions ({$chargingsQuery.data.length} sessions)
				</h2>
			</div>
			<div class="p-4">
				<p class="text-sm text-muted-foreground">
					Charging table and charts will be implemented here
				</p>
			</div>
		</div>
	{/if}
</div>
