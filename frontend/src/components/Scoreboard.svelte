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
    if (r >= 1.3) return 'text-green-400';
    if (r >= 1.0) return 'text-white';
    if (r >= 0.8) return 'text-amber-400';
    return 'text-red-400';
  }

  function mapDisplay(name: string | null): string {
    if (!name) return '—';
    const clean = name.replace('de_', '');
    return clean.charAt(0).toUpperCase() + clean.slice(1);
  }
</script>

{#if loading}
  <div class="text-center py-8 text-zinc-500">Loading scoreboard...</div>
{:else if !data}
  <div class="text-center py-8 text-zinc-500">Select a match to view the scoreboard.</div>
{:else}
  <!-- Match header -->
  <div class="flex items-center justify-center gap-6 mb-6">
    <div class="text-right">
      <div class="text-xs uppercase tracking-wider text-blue-400 font-semibold mb-1">Counter-Terrorists</div>
      <div class="text-3xl font-extrabold text-blue-400">{data.score_team ?? '-'}</div>
    </div>
    <div class="text-center px-4">
      <div class="text-xs uppercase tracking-wider text-zinc-500 mb-1">{mapDisplay(data.map_name)}</div>
      {#if data.result === 'win'}
        <span class="px-3 py-1 rounded-full text-xs font-bold bg-green-900 text-green-400">VICTORY</span>
      {:else if data.result === 'loss'}
        <span class="px-3 py-1 rounded-full text-xs font-bold bg-red-900 text-red-400">DEFEAT</span>
      {:else}
        <span class="px-3 py-1 rounded-full text-xs font-bold bg-zinc-800 text-zinc-400">DRAW</span>
      {/if}
    </div>
    <div class="text-left">
      <div class="text-xs uppercase tracking-wider text-amber-400 font-semibold mb-1">Terrorists</div>
      <div class="text-3xl font-extrabold text-amber-400">{data.score_opponent ?? '-'}</div>
    </div>
  </div>

  <!-- CT Side -->
  <div class="mb-4">
    <div class="flex items-center gap-2 mb-2">
      <div class="w-1 h-4 rounded bg-blue-500"></div>
      <span class="text-xs uppercase tracking-wider text-blue-400 font-semibold">Counter-Terrorists</span>
    </div>
    <div class="overflow-x-auto">
      <table class="w-full text-sm">
        <thead>
          <tr class="text-xs uppercase tracking-wider text-zinc-500 border-b border-white border-opacity-10">
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
            <tr class={p.is_self ? 'bg-purple-950 border-l-2 border-l-purple-500' : 'border-b border-white border-opacity-5'}>
              <td class="py-2 px-3 font-medium">
                {#if p.is_self}
                  <span class="text-purple-400">{p.player_name}</span>
                {:else}
                  {p.player_name}
                {/if}
              </td>
              <td class="text-center py-2 px-2 text-green-400 font-semibold">{p.kills}</td>
              <td class="text-center py-2 px-2 text-red-400">{p.deaths}</td>
              <td class="text-center py-2 px-2 text-zinc-400">{p.assists}</td>
              <td class="text-center py-2 px-2">{p.adr.toFixed(1)}</td>
              <td class="text-center py-2 px-2">{p.headshot_pct.toFixed(0)}%</td>
              <td class={`text-center py-2 px-2 font-bold ${ratingColor(p.rating)}`}>{p.rating.toFixed(2)}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  </div>

  <!-- T Side -->
  <div>
    <div class="flex items-center gap-2 mb-2">
      <div class="w-1 h-4 rounded bg-amber-500"></div>
      <span class="text-xs uppercase tracking-wider text-amber-400 font-semibold">Terrorists</span>
    </div>
    <div class="overflow-x-auto">
      <table class="w-full text-sm">
        <thead>
          <tr class="text-xs uppercase tracking-wider text-zinc-500 border-b border-white border-opacity-10">
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
            <tr class={p.is_self ? 'bg-purple-950 border-l-2 border-l-purple-500' : 'border-b border-white border-opacity-5'}>
              <td class="py-2 px-3 font-medium">
                {#if p.is_self}
                  <span class="text-purple-400">{p.player_name}</span>
                {:else}
                  {p.player_name}
                {/if}
              </td>
              <td class="text-center py-2 px-2 text-green-400 font-semibold">{p.kills}</td>
              <td class="text-center py-2 px-2 text-red-400">{p.deaths}</td>
              <td class="text-center py-2 px-2 text-zinc-400">{p.assists}</td>
              <td class="text-center py-2 px-2">{p.adr.toFixed(1)}</td>
              <td class="text-center py-2 px-2">{p.headshot_pct.toFixed(0)}%</td>
              <td class={`text-center py-2 px-2 font-bold ${ratingColor(p.rating)}`}>{p.rating.toFixed(2)}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  </div>
{/if}
