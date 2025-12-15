<script lang="ts">
	import '../app.css';
	import favicon from '$lib/assets/favicon.svg';
	import Navigation from '$lib/components/Navigation.svelte';
	import { QueryClient, QueryClientProvider } from '@tanstack/svelte-query';

	let { children } = $props();

	// Create QueryClient for data fetching
	const queryClient = new QueryClient({
		defaultOptions: {
			queries: {
				staleTime: 60_000, // 1 minute
				retry: 1
			}
		}
	});
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
	<title>PSA Car Controller</title>
</svelte:head>

<QueryClientProvider client={queryClient}>
	<div class="min-h-screen bg-background">
		<Navigation />
		<main class="container mx-auto px-4 py-6">
			{@render children()}
		</main>
	</div>
</QueryClientProvider>
