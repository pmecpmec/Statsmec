<script lang="ts">
  import { onMount } from 'svelte';

  let { apiUrl = 'http://127.0.0.1:8000/api/v1' } = $props();

  type ClassicStats = {
    total_kills: number;
    total_deaths: number;
    kd: number;
    total_wins: number;
    total_time_hours: number;
  };

  let stats: ClassicStats | null = $state(null);
  let error = $state('');

  onMount(async () => {
    try {
      const res = await fetch(`${apiUrl}/me/csgo-classic`);
      if (!res.ok) {
        error = 'Could not load classic stats.';
        return;
      }
      stats = await res.json();
    } catch {
      error = 'Could not load classic stats.';
    }
  });
</script>

<h3 class="mb-4 font-display text-lg font-semibold text-game-primary">CS2 classic stats</h3>

{#if error}
  <p class="text-sm text-red-600">{error}</p>
{:else if !stats}
  <p class="text-sm text-game-muted">Loading classic stats…</p>
{:else}
  <div class="grid grid-cols-2 gap-3 text-sm">
    <div class="flex flex-col">
      <span class="text-xs font-medium uppercase tracking-wider text-game-muted">Total kills</span>
      <span class="text-lg font-semibold text-game-primary">{stats.total_kills.toLocaleString()}</span>
    </div>
    <div class="flex flex-col">
      <span class="text-xs font-medium uppercase tracking-wider text-game-muted">Total deaths</span>
      <span class="text-lg font-semibold text-game-primary">{stats.total_deaths.toLocaleString()}</span>
    </div>
    <div class="flex flex-col">
      <span class="text-xs font-medium uppercase tracking-wider text-game-muted">K/D</span>
      <span class="text-lg font-semibold text-game-accent">{stats.kd.toFixed(2)}</span>
    </div>
    <div class="flex flex-col">
      <span class="text-xs font-medium uppercase tracking-wider text-game-muted">Wins</span>
      <span class="text-lg font-semibold text-game-primary">{stats.total_wins.toLocaleString()}</span>
    </div>
    <div class="col-span-2 flex flex-col">
      <span class="text-xs font-medium uppercase tracking-wider text-game-muted">Total time played</span>
      <span class="text-lg font-semibold text-game-primary">{stats.total_time_hours.toFixed(1)} hours</span>
    </div>
  </div>
{/if}

