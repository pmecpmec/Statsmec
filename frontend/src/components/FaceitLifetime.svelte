<script lang="ts">
  import { onMount } from 'svelte';

  let { apiUrl = 'http://127.0.0.1:8000/api/v1' } = $props();

  type MapSegment = {
    map: string;
    image: string | null;
    matches: number;
    win_rate: number | null;
    kd: number | null;
    hs_pct: number | null;
  };

  type Ban = {
    reason: string | null;
    game: string | null;
    starts_at: string | null;
    ends_at: string | null;
  };

  type FaceitLifetime = {
    available: boolean;
    api_configured: boolean;
    matches: number;
    wins: number;
    win_rate: number | null;
    avg_kd: number | null;
    avg_hs_pct: number | null;
    current_win_streak: number | null;
    longest_win_streak: number | null;
    recent_results: string[];
    segments: MapSegment[];
    bans: Ban[];
    error: string | null;
  };

  let data: FaceitLifetime | null = $state(null);
  let loading = $state(true);
  let error = $state('');

  onMount(async () => {
    try {
      const res = await fetch(`${apiUrl}/me/faceit-lifetime`);
      if (!res.ok) {
        error = 'Could not load FACEIT lifetime stats.';
        return;
      }
      data = await res.json();
    } catch {
      error = 'Could not load FACEIT lifetime stats.';
    } finally {
      loading = false;
    }
  });

  const fmt = (n: number | null, suffix = '') =>
    n === null || n === undefined ? '—' : `${n}${suffix}`;
</script>

<div class="mb-5 flex flex-wrap items-center justify-between gap-3 border-b border-game pb-3">
  <div class="flex items-center gap-2">
    <span class="section-kicker">FACEIT</span>
    <h3 class="font-display text-lg font-semibold text-game-primary">Lifetime</h3>
  </div>
  {#if data?.available}
    <span class="hud-label">{data.matches.toLocaleString()} matches</span>
  {/if}
</div>

{#if loading}
  <p class="text-sm text-game-muted">Loading FACEIT lifetime stats…</p>
{:else if error}
  <p class="text-sm text-game-muted">{error}</p>
{:else if !data || !data.available}
  <p class="text-sm text-game-muted">
    {data?.error ?? 'FACEIT lifetime data is not available right now.'}
  </p>
{:else}
  <div class="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
    <div class="stat-card p-3">
      <span class="hud-label">Win rate</span>
      <span class="font-display text-xl font-semibold text-game-accent">{fmt(data.win_rate, '%')}</span>
    </div>
    <div class="stat-card p-3">
      <span class="hud-label">Avg K/D</span>
      <span class="font-display text-xl font-semibold text-game-primary">{fmt(data.avg_kd)}</span>
    </div>
    <div class="stat-card p-3">
      <span class="hud-label">Avg HS%</span>
      <span class="font-display text-xl font-semibold text-game-primary">{fmt(data.avg_hs_pct, '%')}</span>
    </div>
    <div class="stat-card p-3">
      <span class="hud-label">Wins</span>
      <span class="font-display text-xl font-semibold text-game-primary">{data.wins.toLocaleString()}</span>
    </div>
    <div class="stat-card p-3">
      <span class="hud-label">Win streak</span>
      <span class="font-display text-xl font-semibold text-game-primary">{fmt(data.current_win_streak)}</span>
    </div>
    <div class="stat-card p-3">
      <span class="hud-label">Best streak</span>
      <span class="font-display text-xl font-semibold text-game-primary">{fmt(data.longest_win_streak)}</span>
    </div>
  </div>

  {#if data.recent_results.length}
    <div class="mt-5">
      <span class="hud-label">Recent (oldest → latest)</span>
      <div class="mt-2 flex flex-wrap gap-1.5">
        {#each data.recent_results as r, i (i)}
          <span
            class="flex h-6 w-6 items-center justify-center rounded text-xs font-bold"
            class:bg-cs-green={r === 'W'}
            class:text-black={r === 'W'}
            class:bg-cs-red={r === 'L'}
            class:text-white={r === 'L'}
          >
            {r}
          </span>
        {/each}
      </div>
    </div>
  {/if}

  {#if data.segments.length}
    <div class="mt-6">
      <span class="hud-label">Per-map breakdown</span>
      <div class="mt-2 overflow-x-auto">
        <table class="w-full min-w-[26rem] text-sm">
          <thead>
            <tr class="border-b border-game text-left text-xs uppercase tracking-wider text-game-muted">
              <th class="py-2 pr-3 font-medium">Map</th>
              <th class="py-2 pr-3 text-right font-medium">Matches</th>
              <th class="py-2 pr-3 text-right font-medium">Win&nbsp;%</th>
              <th class="py-2 pr-3 text-right font-medium">K/D</th>
              <th class="py-2 text-right font-medium">HS%</th>
            </tr>
          </thead>
          <tbody>
            {#each data.segments as seg (seg.map)}
              <tr class="border-b border-game/50 last:border-0">
                <td class="py-2 pr-3 font-medium text-game-primary">{seg.map}</td>
                <td class="py-2 pr-3 text-right text-game-muted">{seg.matches}</td>
                <td class="py-2 pr-3 text-right font-mono text-game-accent">{fmt(seg.win_rate, '%')}</td>
                <td class="py-2 pr-3 text-right font-mono text-game-primary">{fmt(seg.kd)}</td>
                <td class="py-2 text-right font-mono text-game-muted">{fmt(seg.hs_pct, '%')}</td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    </div>
  {/if}

  {#if data.bans.length}
    <div class="mt-5 rounded border border-cs-red/40 bg-cs-red/10 p-3">
      <span class="hud-label text-cs-red">Bans</span>
      <ul class="mt-1 space-y-1 text-sm text-game-primary">
        {#each data.bans as ban, i (i)}
          <li>{ban.reason ?? 'Ban'}{ban.game ? ` · ${ban.game}` : ''}{ban.ends_at ? ` · until ${ban.ends_at}` : ''}</li>
        {/each}
      </ul>
    </div>
  {/if}
{/if}
