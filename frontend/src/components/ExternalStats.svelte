<script lang="ts">
  import { onMount } from 'svelte';

  let { apiUrl = 'http://127.0.0.1:8000/api/v1' } = $props();

  type ScrapeSource = {
    available: boolean;
    source: string;
    url: string | null;
    method: string | null;
    status: string | null;
    stats: Record<string, string | number | null>;
  };

  type ExternalStats = {
    csstats: ScrapeSource;
    esea: ScrapeSource;
  };

  let data: ExternalStats | null = $state(null);
  let loading = $state(true);
  let error = $state('');

  onMount(async () => {
    try {
      const res = await fetch(`${apiUrl}/me/external-stats`);
      if (!res.ok) {
        error = 'Could not load external stats.';
        return;
      }
      data = await res.json();
    } catch {
      error = 'Could not load external stats.';
    } finally {
      loading = false;
    }
  });

  const LABELS: Record<string, string> = {
    rating: 'Rating 2.0',
    kd: 'K/D',
    adr: 'ADR',
    hs_pct: 'HS%',
    win_rate: 'Win rate',
    faceit_level: 'FACEIT level',
    premier_season: 'Premier season',
    premier_rating: 'Premier rating',
    premier_best: 'Premier best',
    premier_tier: 'Premier tier',
    rws: 'RWS',
    rank: 'Rank',
  };

  function entries(src: ScrapeSource): [string, string][] {
    return Object.entries(src.stats)
      .filter(([, v]) => v !== null && v !== undefined && v !== '')
      .map(([k, v]) => [
        LABELS[k] ?? k,
        typeof v === 'number' ? v.toLocaleString() : String(v),
      ]);
  }
</script>

<div class="mb-5 flex flex-wrap items-center justify-between gap-3 border-b border-game pb-3">
  <div class="flex items-center gap-2">
    <span class="section-kicker">External</span>
    <h3 class="font-display text-lg font-semibold text-game-primary">Third-party stats</h3>
  </div>
  <span class="hud-label">best-effort scrape</span>
</div>

{#if loading}
  <p class="text-sm text-game-muted">Loading external stats…</p>
{:else if error || !data}
  <p class="text-sm text-game-muted">{error || 'External stats are not available right now.'}</p>
{:else}
  <div class="grid gap-4 md:grid-cols-2">
    {#each [data.csstats, data.esea] as src (src.source)}
      <div class="border border-game bg-game-muted/40 p-4" style="border-radius: var(--radius-card);">
        <div class="mb-3 flex items-center justify-between gap-2">
          <a
            href={src.url ?? '#'}
            target="_blank"
            rel="noopener noreferrer"
            class="font-display text-sm font-semibold text-game-primary hover:text-game-accent"
          >
            {src.source}
          </a>
          {#if src.available}
            <span class="rounded bg-cs-green/15 px-2 py-0.5 text-xs font-semibold text-cs-green">live</span>
          {:else}
            <span class="rounded bg-game-secondary px-2 py-0.5 text-xs font-semibold text-game-muted">unavailable</span>
          {/if}
        </div>

        {#if src.available}
          <dl class="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
            {#each entries(src) as [label, value] (label)}
              <div class="flex flex-col">
                <dt class="hud-label">{label}</dt>
                <dd class="font-semibold text-game-primary">{value}</dd>
              </div>
            {/each}
          </dl>
        {:else}
          <p class="text-xs leading-relaxed text-game-muted">
            Couldn't fetch — this site is Cloudflare-protected and didn't return
            parseable data.
          </p>
        {/if}
      </div>
    {/each}
  </div>
  <p class="mt-3 text-[0.7rem] leading-relaxed text-game-muted">
    Scraped on a best-effort basis and cached. Numbers come straight from the source page when reachable; nothing is fabricated.
  </p>
{/if}
