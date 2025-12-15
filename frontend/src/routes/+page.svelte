<script lang="ts">
	import { createVehiclesQuery, createTripsQuery, createChargingsQuery } from '$lib/api/queries';

	// Fetch data
	const vehiclesQuery = createVehiclesQuery();
	const tripsQuery = createTripsQuery();
	const chargingsQuery = createChargingsQuery();
</script>

<div class="space-y-6">
	<div>
		<h1 class="text-3xl font-bold">Dashboard</h1>
		<p class="text-muted-foreground">Welcome to PSA Car Controller</p>
	</div>

	<!-- Summary Cards -->
	<div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
		<div class="rounded-lg border bg-card p-6">
			<h3 class="text-sm font-medium text-muted-foreground">Vehicles</h3>
			<p class="mt-2 text-3xl font-bold">
				{#if $vehiclesQuery.isLoading}
					<span class="text-muted-foreground">...</span>
				{:else if $vehiclesQuery.data}
					{$vehiclesQuery.data.length}
				{:else}
					0
				{/if}
			</p>
		</div>

		<div class="rounded-lg border bg-card p-6">
			<h3 class="text-sm font-medium text-muted-foreground">Total Trips</h3>
			<p class="mt-2 text-3xl font-bold">
				{#if $tripsQuery.isLoading}
					<span class="text-muted-foreground">...</span>
				{:else if $tripsQuery.data}
					{$tripsQuery.data.length}
				{:else}
					0
				{/if}
			</p>
		</div>

		<div class="rounded-lg border bg-card p-6">
			<h3 class="text-sm font-medium text-muted-foreground">Charging Sessions</h3>
			<p class="mt-2 text-3xl font-bold">
				{#if $chargingsQuery.isLoading}
					<span class="text-muted-foreground">...</span>
				{:else if $chargingsQuery.data}
					{$chargingsQuery.data.length}
				{:else}
					0
				{/if}
			</p>
		</div>

		<div class="rounded-lg border bg-card p-6">
			<h3 class="text-sm font-medium text-muted-foreground">Status</h3>
			<p class="mt-2 text-3xl font-bold text-green-600">
				{#if $vehiclesQuery.isSuccess}
					Connected
				{:else}
					<span class="text-muted-foreground">...</span>
				{/if}
			</p>
		</div>
	</div>

	<!-- Vehicles List -->
	{#if $vehiclesQuery.isSuccess && $vehiclesQuery.data}
		<div class="rounded-lg border bg-card">
			<div class="border-b p-4">
				<h2 class="text-lg font-semibold">Your Vehicles</h2>
			</div>
			<div class="divide-y">
				{#each $vehiclesQuery.data as vehicle}
					<div class="p-4">
						<div class="flex items-center justify-between">
							<div>
								<h3 class="font-medium">{vehicle.label}</h3>
								<p class="text-sm text-muted-foreground">{vehicle.vin}</p>
							</div>
							<div class="text-right">
								<p class="text-sm font-medium">{vehicle.brand}</p>
								{#if vehicle.status?.energy?.[0]}
									<p class="text-sm text-muted-foreground">
										Battery: {vehicle.status.energy[0].level}%
									</p>
								{/if}
							</div>
						</div>
					</div>
				{/each}
			</div>
		</div>
	{:else if $vehiclesQuery.isError}
		<div class="rounded-lg border border-destructive bg-destructive/10 p-4">
			<p class="text-sm text-destructive">
				Error loading vehicles: {$vehiclesQuery.error?.message}
			</p>
		</div>
	{/if}
</div>
