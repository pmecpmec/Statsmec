<script lang="ts">
  import { onMount, onDestroy } from 'svelte';

  let { apiUrl = 'http://127.0.0.1:8000/api/v1' } = $props();

  type Status = {
    status: string;
    current_match_id: number | null;
    last_match_id: number | null;
    last_match_ago: string | null;
    total_matches: number;
  };

  let data: Status | null = $state(null);
  let interval: ReturnType<typeof setInterval> | null = $state(null);

  async function poll() {
    try {
      const res = await fetch(`${apiUrl}/me/status`);
      data = await res.json();
    } catch {
      /* backend offline */
    }
  }

  onMount(() => {
    poll();
    interval = setInterval(poll, 30000);
  });

  onDestroy(() => {
    if (interval) clearInterval(interval);
  });
</script>

{#if data}
  <div class="flex items-center gap-3 px-4 py-2 rounded-full border border-white border-opacity-10" style="background: rgba(255,255,255,0.04);">
    {#if data.status === 'in_game'}
      <span class="relative flex h-3 w-3">
        <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
        <span class="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
      </span>
      <span class="text-sm font-semibold text-green-400">LIVE — In Game</span>
    {:else if data.status === 'online'}
      <span class="relative flex h-3 w-3">
        <span class="relative inline-flex rounded-full h-3 w-3 bg-blue-500"></span>
      </span>
      <span class="text-sm text-zinc-400">
        Online
        {#if data.last_match_ago}
          <span class="text-zinc-600">· last match {data.last_match_ago}</span>
        {/if}
      </span>
    {:else}
      <span class="relative flex h-3 w-3">
        <span class="relative inline-flex rounded-full h-3 w-3 bg-zinc-600"></span>
      </span>
      <span class="text-sm text-zinc-500">Offline</span>
    {/if}
  </div>
{/if}
