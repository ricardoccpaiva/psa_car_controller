<script lang="ts">
	import { page } from '$app/stores';

	const navItems = [
		{ href: '/', label: 'Dashboard' },
		{ href: '/trips', label: 'Trips' },
		{ href: '/charging', label: 'Charging' },
		{ href: '/map', label: 'Map' },
		{ href: '/control', label: 'Control' },
		{ href: '/config', label: 'Settings' }
	];

	let currentPath = $derived($page.url.pathname);
</script>

<nav class="border-b bg-background">
	<div class="container mx-auto px-4">
		<div class="flex h-16 items-center justify-between">
			<!-- Logo/Title -->
			<div class="flex items-center gap-2">
				<a href="/" class="text-xl font-bold text-primary hover:text-primary/80">
					PSA Car Controller
				</a>
				<span class="rounded-md bg-primary/10 px-2 py-1 text-xs font-medium text-primary">
					Modern
				</span>
			</div>

			<!-- Desktop Navigation -->
			<div class="hidden md:flex md:items-center md:gap-1">
				{#each navItems as item}
					<a
						href={item.href}
						class="rounded-md px-3 py-2 text-sm font-medium transition-colors
							{currentPath === item.href
							? 'bg-primary text-primary-foreground'
							: 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'}"
					>
						{item.label}
					</a>
				{/each}
			</div>

			<!-- Mobile Menu Button -->
			<button class="md:hidden rounded-md p-2 hover:bg-accent">
				<svg
					class="h-6 w-6"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M4 6h16M4 12h16M4 18h16"
					/>
				</svg>
			</button>
		</div>

		<!-- Mobile Navigation -->
		<div class="md:hidden pb-4 space-y-1">
			{#each navItems as item}
				<a
					href={item.href}
					class="block rounded-md px-3 py-2 text-base font-medium transition-colors
						{currentPath === item.href
						? 'bg-primary text-primary-foreground'
						: 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'}"
				>
					{item.label}
				</a>
			{/each}
		</div>
	</div>
</nav>
