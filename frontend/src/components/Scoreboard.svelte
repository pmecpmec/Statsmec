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
    if (r >= 1.3) return 'text-win';
    if (r >= 1.0) return 'text-game-primary';
    if (r >= 0.8) return 'text-t';
    return 'text-loss';
  }

  function mapDisplay(name: string | null): string {
    if (!name) return '—';
    const clean = name.replace('de_', '');
    return clean.charAt(0).toUpperCase() + clean.slice(1);
  }
</script>

{#snippet teamTable(players: Player[], side: 'ct' | 't')}
  {@const isCt = side === 'ct'}
  <div class="overflow-hidden rounded-md border border-game">
    <div
      class="flex items-center gap-2 px-3 py-2"
      style={`background: ${isCt ? 'var(--ct-soft)' : 'var(--t-soft)'}; border-bottom: 1px solid ${isCt ? 'var(--ct-line)' : 'var(--t-line)'};`}
    >
      <span class="h-3.5 w-1 rounded-sm" style={`background: ${isCt ? 'var(--ct-bright)' : 'var(--t-bright)'};`}></span>
      <span class={`font-mono text-xs font-bold uppercase tracking-[0.2em] ${isCt ? 'text-ct' : 'text-t'}`}>
        {isCt ? 'Counter-Terrorists' : 'Terrorists'}
      </span>
    </div>
    <div class="overflow-x-auto">
      <table class="w-full text-sm">
        <thead>
          <tr class="hud-label border-b border-game">
            <th class="w-40 px-3 py-2 text-left">Player</th>
            <th class="px-2 py-2 text-center">K</th>
            <th class="px-2 py-2 text-center">D</th>
            <th class="px-2 py-2 text-center">A</th>
            <th class="px-2 py-2 text-center">ADR</th>
            <th class="px-2 py-2 text-center">HS%</th>
            <th class="px-2 py-2 text-center">Rating</th>
          </tr>
        </thead>
        <tbody>
          {#each players as p (p.player_name)}
            <tr
              class={p.is_self
                ? 'border-b border-game bg-[var(--accent-soft)]/40 transition-colors'
                : 'border-b border-game transition-colors hover:bg-game-muted/40'}
              style={p.is_self ? `box-shadow: inset 3px 0 0 ${isCt ? 'var(--ct-bright)' : 'var(--t-bright)'};` : ''}
            >
              <td class="px-3 py-2 font-medium">
                {#if p.is_self}
                  <span class="font-semibold text-game-accent">{p.player_name}</span>
                {:else}
                  <span class="text-game-secondary">{p.player_name}</span>
                {/if}
              </td>
              <td class="px-2 py-2 text-center font-semibold text-win">{p.kills}</td>
              <td class="px-2 py-2 text-center text-loss">{p.deaths}</td>
              <td class="px-2 py-2 text-center text-game-muted">{p.assists}</td>
              <td class="px-2 py-2 text-center text-game-primary">{p.adr.toFixed(1)}</td>
              <td class="px-2 py-2 text-center text-game-secondary">{p.headshot_pct.toFixed(0)}%</td>
              <td class={`px-2 py-2 text-center font-mono font-bold ${ratingColor(p.rating)}`}>{p.rating.toFixed(2)}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  </div>
{/snippet}

{#if loading}
  <div class="py-8 text-center text-sm text-game-muted">Loading scoreboard…</div>
{:else if !data}
  <div class="py-8 text-center text-sm text-game-muted">Select a match to view the scoreboard.</div>
{:else}
  <!-- Broadcast-style match header -->
  <div
    class="mb-6 grid grid-cols-[1fr_auto_1fr] items-center gap-4 overflow-hidden rounded-md border border-game px-4 py-4"
    style="background: linear-gradient(90deg, var(--ct-soft), transparent 35%, transparent 65%, var(--t-soft));"
  >
    <div class="text-right">
      <div class="font-mono text-[0.65rem] font-bold uppercase tracking-[0.2em] text-ct">Counter-Terrorists</div>
      <div class="font-mono text-4xl font-extrabold leading-none text-ct">{data.score_team ?? '-'}</div>
    </div>
    <div class="flex flex-col items-center px-2 text-center">
      <span class="hud-label">{mapDisplay(data.map_name)}</span>
      {#if data.result === 'win'}
        <span class="badge-win mt-1">Victory</span>
      {:else if data.result === 'loss'}
        <span class="badge-loss mt-1">Defeat</span>
      {:else}
        <span class="mt-1 rounded-md bg-game-muted px-3 py-1 text-xs font-bold uppercase tracking-wide text-game-muted">Draw</span>
      {/if}
    </div>
    <div class="text-left">
      <div class="font-mono text-[0.65rem] font-bold uppercase tracking-[0.2em] text-t">Terrorists</div>
      <div class="font-mono text-4xl font-extrabold leading-none text-t">{data.score_opponent ?? '-'}</div>
    </div>
  </div>

  <div class="space-y-4">
    {@render teamTable(data.ct, 'ct')}
    {@render teamTable(data.t, 't')}
  </div>
{/if}
