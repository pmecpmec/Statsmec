<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { showDevSetupHints } from '../lib/devHints';

  let {
    apiUrl = 'http://127.0.0.1:8000/api/v1',
    /** Hide Sync FACEIT on public builds when the API is not configured (see ProfileHero). */
    faceitSyncVisible = true,
  } = $props();

  type Status = {
    status: string;
    current_match_id: number | null;
    last_match_id: number | null;
    last_match_ago: string | null;
    total_matches: number;
  };

  let data: Status | null = $state(null);
  let syncing = $state(false);
  let syncMsg = $state('');
  let interval: ReturnType<typeof setInterval> | null = $state(null);

  async function poll() {
    try {
      const res = await fetch(`${apiUrl}/me/status`);
      data = await res.json();
    } catch {
      /* backend offline */
    }
  }

  async function triggerSync() {
    syncing = true;
    syncMsg = '';
    try {
      const res = await fetch(`${apiUrl}/me/sync`, { method: 'POST' });
      const result = await res.json();
      syncMsg = result.message;
      if (result.success) {
        await poll();
        setTimeout(() => {
          syncMsg = '';
        }, 3000);
      }
    } catch {
      syncMsg = showDevSetupHints ? 'Backend offline' : 'Could not sync. Try again later.';
    }
    syncing = false;
  }

  onMount(() => {
    poll();
    interval = setInterval(poll, 30000);
  });

  onDestroy(() => {
    if (interval) clearInterval(interval);
  });
</script>

<div class="flex flex-wrap items-center justify-center gap-3">
  {#if data}
    <div
      class="flex items-center gap-2 rounded-full border border-stone-200 bg-white px-4 py-2 shadow-sm"
    >
      {#if data.status === 'in_game'}
        <span class="relative flex h-3 w-3">
          <span class="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75"></span>
          <span class="relative inline-flex h-3 w-3 rounded-full bg-emerald-500"></span>
        </span>
        <span class="text-sm font-semibold text-emerald-700">Live — in game</span>
      {:else if data.status === 'online'}
        <span class="relative inline-flex h-3 w-3 rounded-full bg-sky-500"></span>
        <span class="text-sm text-game-muted">
          {data.total_matches} matches
          {#if data.last_match_ago}
            <span class="text-stone-400"> · last {data.last_match_ago}</span>
          {/if}
        </span>
      {:else}
        <span class="relative inline-flex h-3 w-3 rounded-full bg-stone-400"></span>
        <span class="text-sm text-game-muted">Offline</span>
      {/if}
    </div>
  {/if}

  {#if faceitSyncVisible}
    <button
      class="rounded-full border border-[var(--accent)]/40 bg-[var(--accent-soft)] px-4 py-2 text-xs font-semibold text-game-accent transition-colors hover:bg-[var(--accent)]/15 disabled:opacity-50"
      onclick={triggerSync}
      disabled={syncing}
    >
      {syncing ? 'Syncing…' : 'Sync FACEIT'}
    </button>

    {#if syncMsg}
      <span class="text-xs text-game-muted">{syncMsg}</span>
    {/if}
  {/if}
</div>
