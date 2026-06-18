<script lang="ts">
  type Player = {
    player_name: string;
    team: string;
    is_self: boolean;
    kills: number;
    deaths: number;
    assists: number;
    adr: number;
    headshot_pct: number;
    rating: number;
  };

  type ScoreboardData = {
    match_id: number;
    map_name: string | null;
    score_team: number | null;
    score_opponent: number | null;
    result: string | null;
    ct: Player[];
    t: Player[];
  };

  let { data = null as ScoreboardData | null, loading = false } = $props();

  function ratingColor(r: number): string {
    if (r >= 1.3) return 'text-emerald-700';
    if (r >= 1.0) return 'text-game-primary';
    if (r >= 0.8) return 'text-amber-700';
    return 'text-red-600';
  }

  function mapDisplay(name: string | null): string {
    if (!name) return '—';
    const clean = name.replace('de_', '');
    return clean.charAt(0).toUpperCase() + clean.slice(1);
  }
</script>

{#if loading}
  <div class="py-8 text-center text-sm text-game-muted">Loading scoreboard…</div>
{:else if !data}
  <div class="py-8 text-center text-sm text-game-muted">Select a match to view the scoreboard.</div>
{:else}
  <!-- Match header -->
  <div class="mb-6 flex items-center justify-center gap-6">
    <div class="text-right">
      <div class="mb-1 text-xs font-semibold uppercase tracking-wider text-sky-700">Counter-Terrorists</div>
      <div class="text-3xl font-extrabold text-sky-600">{data.score_team ?? '-'}</div>
    </div>
    <div class="px-4 text-center">
      <div class="mb-1 text-xs uppercase tracking-wider text-game-muted">{mapDisplay(data.map_name)}</div>
      {#if data.result === 'win'}
        <span class="rounded-full bg-emerald-100 px-3 py-1 text-xs font-bold text-emerald-800">Victory</span>
      {:else if data.result === 'loss'}
        <span class="rounded-full bg-red-100 px-3 py-1 text-xs font-bold text-red-800">Defeat</span>
      {:else}
        <span class="rounded-full bg-game-muted px-3 py-1 text-xs font-bold text-game-muted">Draw</span>
      {/if}
    </div>
    <div class="text-left">
      <div class="mb-1 text-xs font-semibold uppercase tracking-wider text-amber-800">Terrorists</div>
      <div class="text-3xl font-extrabold text-amber-700">{data.score_opponent ?? '-'}</div>
    </div>
  </div>

  <!-- CT Side -->
  <div class="mb-4">
    <div class="mb-2 flex items-center gap-2">
      <div class="h-4 w-1 rounded bg-sky-500"></div>
      <span class="text-xs font-semibold uppercase tracking-wider text-sky-700">Counter-Terrorists</span>
    </div>
    <div class="overflow-x-auto">
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b border-game text-xs font-medium uppercase tracking-wider text-game-muted">
            <th class="text-left py-2 px-3 w-40">Player</th>
            <th class="text-center py-2 px-2">K</th>
            <th class="text-center py-2 px-2">D</th>
            <th class="text-center py-2 px-2">A</th>
            <th class="text-center py-2 px-2">ADR</th>
            <th class="text-center py-2 px-2">HS%</th>
            <th class="text-center py-2 px-2">Rating</th>
          </tr>
        </thead>
        <tbody>
          {#each data.ct as p}
            <tr
              class={p.is_self
                ? 'border-b border-game border-l-2 border-l-[var(--accent)] bg-[var(--accent-soft)]/30'
                : 'border-b border-game'}
            >
              <td class="px-3 py-2 font-medium">
                {#if p.is_self}
                  <span class="font-semibold text-game-accent">{p.player_name}</span>
                {:else}
                  {p.player_name}
                {/if}
              </td>
              <td class="px-2 py-2 text-center font-semibold text-emerald-700">{p.kills}</td>
              <td class="px-2 py-2 text-center text-red-600">{p.deaths}</td>
              <td class="px-2 py-2 text-center text-game-muted">{p.assists}</td>
              <td class="px-2 py-2 text-center text-game-primary">{p.adr.toFixed(1)}</td>
              <td class="px-2 py-2 text-center text-game-primary">{p.headshot_pct.toFixed(0)}%</td>
              <td class={`px-2 py-2 text-center font-bold ${ratingColor(p.rating)}`}>{p.rating.toFixed(2)}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  </div>

  <!-- T Side -->
  <div>
    <div class="mb-2 flex items-center gap-2">
      <div class="h-4 w-1 rounded bg-amber-500"></div>
      <span class="text-xs font-semibold uppercase tracking-wider text-amber-800">Terrorists</span>
    </div>
    <div class="overflow-x-auto">
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b border-game text-xs font-medium uppercase tracking-wider text-game-muted">
            <th class="text-left py-2 px-3 w-40">Player</th>
            <th class="text-center py-2 px-2">K</th>
            <th class="text-center py-2 px-2">D</th>
            <th class="text-center py-2 px-2">A</th>
            <th class="text-center py-2 px-2">ADR</th>
            <th class="text-center py-2 px-2">HS%</th>
            <th class="text-center py-2 px-2">Rating</th>
          </tr>
        </thead>
        <tbody>
          {#each data.t as p}
            <tr
              class={p.is_self
                ? 'border-b border-game border-l-2 border-l-[var(--accent)] bg-[var(--accent-soft)]/30'
                : 'border-b border-game'}
            >
              <td class="px-3 py-2 font-medium">
                {#if p.is_self}
                  <span class="font-semibold text-game-accent">{p.player_name}</span>
                {:else}
                  {p.player_name}
                {/if}
              </td>
              <td class="px-2 py-2 text-center font-semibold text-emerald-700">{p.kills}</td>
              <td class="px-2 py-2 text-center text-red-600">{p.deaths}</td>
              <td class="px-2 py-2 text-center text-game-muted">{p.assists}</td>
              <td class="px-2 py-2 text-center text-game-primary">{p.adr.toFixed(1)}</td>
              <td class="px-2 py-2 text-center text-game-primary">{p.headshot_pct.toFixed(0)}%</td>
              <td class={`px-2 py-2 text-center font-bold ${ratingColor(p.rating)}`}>{p.rating.toFixed(2)}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  </div>
{/if}
