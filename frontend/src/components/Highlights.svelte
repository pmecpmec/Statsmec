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
  <p class="text-zinc-500 text-sm">Could not load highlights.</p>
{:else if data && data.clips.length > 0}
  <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
    {#each data.clips as clip, i (clip.clip_id ?? `clip-${i}`)}
      <a
        href={clip.url ?? '#'}
        target="_blank"
        rel="noopener noreferrer"
        class="group block rounded-xl overflow-hidden border border-white/10 bg-black/20 hover:border-primary-500/50 transition-colors"
      >
        <div class="aspect-video bg-zinc-800 relative">
          {#if clip.thumbnail}
            <img
              src={clip.thumbnail}
              alt={clip.title}
              class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
            />
          {:else}
            <div class="w-full h-full flex items-center justify-center text-zinc-500 text-4xl">▶</div>
          {/if}
        </div>
        <div class="p-3">
          <p class="text-sm font-semibold text-zinc-200 truncate" title={clip.title}>{clip.title}</p>
          {#if clip.map || clip.kills != null}
            <p class="text-xs text-zinc-500 mt-0.5">
              {[clip.map, clip.kills != null ? `${clip.kills}K` : null].filter(Boolean).join(' · ')}
            </p>
          {/if}
        </div>
      </a>
    {/each}
  </div>
  {#if data.total > data.clips.length}
    <p class="text-zinc-500 text-xs mt-3">{data.total} total clips on Allstar</p>
  {/if}
{:else if data && data.clips.length === 0}
  <p class="text-zinc-500 text-sm">No highlights yet.</p>
{:else}
  <p class="text-zinc-500 text-sm">Loading highlights…</p>
{/if}
