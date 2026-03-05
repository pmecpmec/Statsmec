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

<h3 class="text-lg font-bold text-white mb-4">CS:GO / Classic Stats</h3>

{#if error}
  <p class="text-red-400 text-sm">{error}</p>
{:else if !stats}
  <p class="text-zinc-500 text-sm">Loading classic stats…</p>
{:else}
  <div class="grid grid-cols-2 gap-3 text-sm">
    <div class="flex flex-col">
      <span class="text-xs uppercase tracking-wider text-zinc-500">Total Kills</span>
      <span class="text-lg font-semibold">{stats.total_kills.toLocaleString()}</span>
    </div>
    <div class="flex flex-col">
      <span class="text-xs uppercase tracking-wider text-zinc-500">Total Deaths</span>
      <span class="text-lg font-semibold">{stats.total_deaths.toLocaleString()}</span>
    </div>
    <div class="flex flex-col">
      <span class="text-xs uppercase tracking-wider text-zinc-500">K/D</span>
      <span class="text-lg font-semibold">{stats.kd.toFixed(2)}</span>
    </div>
    <div class="flex flex-col">
      <span class="text-xs uppercase tracking-wider text-zinc-500">Wins</span>
      <span class="text-lg font-semibold">{stats.total_wins.toLocaleString()}</span>
    </div>
    <div class="flex flex-col col-span-2">
      <span class="text-xs uppercase tracking-wider text-zinc-500">Total Time Played</span>
      <span class="text-lg font-semibold">{stats.total_time_hours.toFixed(1)} hours</span>
    </div>
  </div>
{/if}

