<script lang="ts">
  import { onMount } from 'svelte';

  let { apiUrl = 'http://127.0.0.1:8000/api/v1', limit = 12 } = $props();

  type Clip = {
    clip_id: string | null;
    title: string;
    url: string | null;
    thumbnail: string | null;
    created_at: string | null;
    status?: string | null;
    steam_id?: string | null;
    map?: string | null;
    kills?: number | null;
    headshots?: number | null;
    weapon?: string | null;
  };

  type HighlightsData = { total: number; clips: Clip[] };

  let data: HighlightsData | null = $state(null);
  let error = $state(false);

  onMount(async () => {
    try {
      const res = await fetch(`${apiUrl}/me/highlights?limit=${limit}`);
      if (res.ok) data = await res.json();
      else error = true;
    } catch {
      error = true;
    }
  });
</script>

{#if error}
  <p class="text-sm text-game-muted">Could not load highlights.</p>
{:else if data && data.clips.length > 0}
  <div class="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4">
    {#each data.clips as clip, i (clip.clip_id ?? `clip-${i}`)}
      <a
        href={clip.url ?? '#'}
        target="_blank"
        rel="noopener noreferrer"
        class="group block overflow-hidden border border-game bg-game-card shadow-sm transition-all hover:border-[var(--accent)]/35 hover:shadow-md"
        style="border-radius: var(--radius-card);"
      >
        <div class="relative aspect-video bg-game-muted">
          {#if clip.thumbnail}
            <img
              src={clip.thumbnail}
              alt={clip.title}
              class="h-full w-full object-cover transition-transform duration-200 group-hover:scale-105"
            />
          {:else}
            <div class="flex h-full w-full items-center justify-center text-4xl text-game-muted">▶</div>
          {/if}
        </div>
        <div class="p-3">
          <p class="truncate text-sm font-semibold text-game-primary" title={clip.title}>{clip.title}</p>
          {#if clip.map || clip.kills != null}
            <p class="mt-0.5 text-xs text-game-muted">
              {[clip.map, clip.kills != null ? `${clip.kills}K` : null].filter(Boolean).join(' · ')}
            </p>
          {/if}
        </div>
      </a>
    {/each}
  </div>
  {#if data.total > data.clips.length}
    <p class="mt-3 text-xs text-game-muted">{data.total} total clips on Allstar</p>
  {/if}
{:else if data && data.clips.length === 0}
  <p class="text-sm text-game-muted">No highlights yet.</p>
{:else}
  <p class="text-sm text-game-muted">Loading highlights…</p>
{/if}
