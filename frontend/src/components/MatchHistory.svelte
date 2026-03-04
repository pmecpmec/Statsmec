<script lang="ts">
  import { onMount } from 'svelte';

  let { apiUrl = 'http://127.0.0.1:8000/api/v1' } = $props();

  type Match = {
    id: number;
    external_match_id: string;
    provider: string;
    map_name: string | null;
    started_at: string;
    duration_seconds: number | null;
    score_team: number | null;
    score_opponent: number | null;
    result: string | null;
  };

  type Round = {
    id: number;
    round_number: number;
    winning_team: string | null;
    kills: number | null;
    deaths: number | null;
    weapon_used: string | null;
    weapon_stats: { weapon_name: string; shots: number; hits: number; headshots: number }[];
  };

  let matches: Match[] = $state([]);
  let loading = $state(true);
  let error = $state('');
  let selectedId: number | null = $state(null);
  let rounds: Round[] = $state([]);
  let roundsLoading = $state(false);

  function mapDisplay(name: string | null): string {
    if (!name) return '—';
    const clean = name.replace('de_', '');
    return clean.charAt(0).toUpperCase() + clean.slice(1);
  }

  function timeAgo(iso: string): string {
    const diff = Date.now() - new Date(iso).getTime();
    const h = Math.floor(diff / 3600000);
    if (h < 1) return 'just now';
    if (h < 24) return `${h}h ago`;
    const d = Math.floor(h / 24);
    return d === 1 ? 'yesterday' : `${d}d ago`;
  }

  function rowClass(id: number): string {
    const base = 'border-b border-white border-opacity-5 cursor-pointer transition-colors';
    if (id === selectedId) return base + ' bg-purple-900 border-l-2 border-l-purple-500';
    return base + ' hover:bg-purple-950';
  }

  function killClass(k: number | null): string {
    return (k ?? 0) > 0 ? 'py-1.5 px-2 text-green-400 font-semibold' : 'py-1.5 px-2';
  }

  function deathClass(d: number | null): string {
    return (d ?? 0) > 0 ? 'py-1.5 px-2 text-red-400' : 'py-1.5 px-2';
  }

  async function loadRounds(matchId: number) {
    selectedId = matchId;
    roundsLoading = true;
    try {
      const res = await fetch(`${apiUrl}/users/1/matches/${matchId}/rounds`);
      rounds = await res.json();
    } catch {
      rounds = [];
    }
    roundsLoading = false;
  }

  onMount(async () => {
    try {
      const res = await fetch(`${apiUrl}/users/1/matches?limit=20`);
      matches = await res.json();
      if (matches.length) loadRounds(matches[0].id);
    } catch {
      error = 'Could not load matches. Is the backend running?';
    }
    loading = false;
  });
</script>

{#if loading}
  <p class="text-zinc-500 text-center py-8">Loading matches...</p>
{:else if error}
  <p class="text-red-400 text-center py-8">{error}</p>
{:else}
  <div class="overflow-x-auto">
    <table class="w-full text-sm">
      <thead>
        <tr class="text-xs uppercase tracking-wider text-zinc-500 border-b border-white border-opacity-10">
          <th class="text-left py-3 px-3">When</th>
          <th class="text-left py-3 px-3">Map</th>
          <th class="text-left py-3 px-3">Score</th>
          <th class="text-left py-3 px-3">Result</th>
          <th class="text-left py-3 px-3">Duration</th>
        </tr>
      </thead>
      <tbody>
        {#each matches as m (m.id)}
          <tr class={rowClass(m.id)} onclick={() => loadRounds(m.id)}>
            <td class="py-2.5 px-3 text-zinc-400">{timeAgo(m.started_at)}</td>
            <td class="py-2.5 px-3 font-medium">{mapDisplay(m.map_name)}</td>
            <td class="py-2.5 px-3">
              <span class={m.result === 'win' ? 'text-green-400 font-semibold' : 'text-red-400 font-semibold'}>
                {m.score_team ?? '-'}
              </span>
              <span class="text-zinc-600 mx-1">:</span>
              <span>{m.score_opponent ?? '-'}</span>
            </td>
            <td class="py-2.5 px-3">
              {#if m.result === 'win'}
                <span class="px-2 py-0.5 rounded text-xs font-bold bg-green-900 text-green-400">W</span>
              {:else if m.result === 'loss'}
                <span class="px-2 py-0.5 rounded text-xs font-bold bg-red-900 text-red-400">L</span>
              {:else}
                <span class="text-zinc-500">-</span>
              {/if}
            </td>
            <td class="py-2.5 px-3 text-zinc-500">
              {m.duration_seconds ? `${Math.round(m.duration_seconds / 60)}m` : '-'}
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>

  {#if selectedId}
    <div class="mt-6 pt-4 border-t border-white border-opacity-10">
      <h4 class="text-sm font-semibold text-zinc-400 mb-3 uppercase tracking-wider">Round Breakdown</h4>
      {#if roundsLoading}
        <p class="text-zinc-500 text-sm">Loading rounds...</p>
      {:else if rounds.length === 0}
        <p class="text-zinc-500 text-sm">No round data for this match.</p>
      {:else}
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr class="text-xs uppercase tracking-wider text-zinc-500 border-b border-white border-opacity-10">
                <th class="text-left py-2 px-2">#</th>
                <th class="text-left py-2 px-2">Side</th>
                <th class="text-left py-2 px-2">K</th>
                <th class="text-left py-2 px-2">D</th>
                <th class="text-left py-2 px-2">Weapon</th>
                <th class="text-left py-2 px-2">Accuracy</th>
              </tr>
            </thead>
            <tbody>
              {#each rounds as r (r.id)}
                <tr class="border-b border-white border-opacity-5">
                  <td class="py-1.5 px-2 text-zinc-500">{r.round_number}</td>
                  <td class="py-1.5 px-2">
                    <span class={r.winning_team === 'CT' ? 'text-blue-400' : 'text-amber-400'}>
                      {r.winning_team ?? '-'}
                    </span>
                  </td>
                  <td class={killClass(r.kills)}>{r.kills ?? 0}</td>
                  <td class={deathClass(r.deaths)}>{r.deaths ?? 0}</td>
                  <td class="py-1.5 px-2 text-zinc-300">{r.weapon_used ?? '-'}</td>
                  <td class="py-1.5 px-2 text-xs text-zinc-500">
                    {#each r.weapon_stats as ws}
                      <span class="mr-2">
                        {ws.hits}/{ws.shots}
                        {#if ws.headshots > 0}
                          <span class="text-amber-400">({ws.headshots} HS)</span>
                        {/if}
                      </span>
                    {/each}
                  </td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      {/if}
    </div>
  {/if}
{/if}
