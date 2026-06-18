<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import Scoreboard from './Scoreboard.svelte';
  import { showDevSetupHints } from '../lib/devHints';

  let {
    apiUrl = 'http://127.0.0.1:8000/api/v1',
    compact = false,
    maxRows = 20,
  } = $props();

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

  type ScoreboardData = {
    match_id: number;
    map_name: string | null;
    score_team: number | null;
    score_opponent: number | null;
    result: string | null;
    ct: any[];
    t: any[];
  };

  let matches: Match[] = $state([]);
  let loading = $state(true);
  let error = $state('');
  let selectedId: number | null = $state(null);
  let scoreboard: ScoreboardData | null = $state(null);
  let scoreboardLoading = $state(false);
  let tab: 'scoreboard' | 'rounds' = $state('scoreboard');
  let pollInterval: ReturnType<typeof setInterval> | null = $state(null);

  type Round = {
    id: number;
    round_number: number;
    winning_team: string | null;
    kills: number | null;
    deaths: number | null;
    weapon_used: string | null;
    weapon_stats: { weapon_name: string; shots: number; hits: number; headshots: number }[];
  };
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
    if (compact) {
      const base = 'border-b border-game transition-colors';
      if (id === selectedId) return base + ' bg-[var(--accent-soft)]/50';
      return base + ' hover:bg-game-muted/40';
    }
    const base = 'cursor-pointer border-b border-game transition-colors';
    if (id === selectedId) return base + ' border-l-2 border-l-[var(--accent)] bg-[var(--accent-soft)]/40';
    return base + ' hover:bg-game-muted/40';
  }

  function killClass(k: number | null): string {
    return (k ?? 0) > 0 ? 'px-2 py-1.5 font-semibold text-emerald-700' : 'px-2 py-1.5';
  }

  function deathClass(d: number | null): string {
    return (d ?? 0) > 0 ? 'px-2 py-1.5 text-red-600' : 'px-2 py-1.5';
  }

  function resultLabel(res: string | null): string {
    if (!res) return '-';
    const v = res.toLowerCase();
    if (v === 'win') return 'W';
    if (v === 'loss') return 'L';
    if (v === 'ct') return 'CT';
    if (v === 't') return 'T';
    return res;
  }

  function resultClass(res: string | null): string {
    const v = (res ?? '').toLowerCase();
    if (v === 'win') return 'badge-win';
    if (v === 'loss') return 'badge-loss';
    return 'text-sm text-game-muted';
  }

  function roundResultClass(res: string | null): string {
    if (res)
      return 'inline-flex rounded-md border border-game bg-game-muted px-2 py-0.5 text-xs font-semibold text-game-primary';
    return 'text-sm text-game-muted';
  }

  async function selectMatch(matchId: number) {
    selectedId = matchId;
    if (tab === 'scoreboard') await loadScoreboard(matchId);
    else await loadRounds(matchId);
  }

  async function loadScoreboard(matchId: number) {
    scoreboardLoading = true;
    try {
      const res = await fetch(`${apiUrl}/users/1/matches/${matchId}/scoreboard`);
      scoreboard = await res.json();
    } catch {
      scoreboard = null;
    }
    scoreboardLoading = false;
  }

  async function loadRounds(matchId: number) {
    roundsLoading = true;
    try {
      const res = await fetch(`${apiUrl}/users/1/matches/${matchId}/rounds`);
      rounds = await res.json();
    } catch {
      rounds = [];
    }
    roundsLoading = false;
  }

  async function switchTab(t: 'scoreboard' | 'rounds') {
    tab = t;
    if (!selectedId) return;
    if (t === 'scoreboard') await loadScoreboard(selectedId);
    else await loadRounds(selectedId);
  }

  let visibleMatches = $derived(compact ? matches.slice(0, maxRows) : matches);

  async function fetchMatches() {
    try {
      const lim = compact ? Math.min(maxRows, 20) : 20;
      const res = await fetch(`${apiUrl}/users/1/matches?limit=${lim}`);
      const newMatches: Match[] = await res.json();
      if (newMatches.length && (!matches.length || newMatches[0].id !== matches[0].id)) {
        matches = newMatches;
        if (!selectedId && matches.length) selectMatch(matches[0].id);
      }
    } catch {
      if (!matches.length) {
        error = showDevSetupHints
          ? 'Could not load matches. Is the backend running?'
          : 'Could not load matches. Try again later.';
      }
    }
  }

  onMount(async () => {
    await fetchMatches();
    if (matches.length && !selectedId && !compact) selectMatch(matches[0].id);
    loading = false;
    if (!compact) pollInterval = setInterval(fetchMatches, 30000);
  });

  onDestroy(() => {
    if (pollInterval) clearInterval(pollInterval);
  });
</script>

{#if loading}
  <p class="py-8 text-center text-sm text-game-muted">Loading matches…</p>
{:else if error}
  <p class="py-8 text-center text-sm {showDevSetupHints ? 'text-red-600' : 'text-game-muted'}">
    {showDevSetupHints ? error : 'No matches to display right now.'}
  </p>
{:else}
  <div class="overflow-x-auto">
    <table class="w-full text-sm">
      <thead>
        <tr class="border-b border-game text-xs font-medium uppercase tracking-wider text-game-muted">
          {#if !compact}
            <th class="px-3 py-3 text-left">When</th>
          {/if}
          <th class="px-3 py-3 text-left">Match</th>
          <th class="px-3 py-3 text-left">Score</th>
          <th class="px-3 py-3 text-left">Status</th>
          {#if !compact}
            <th class="px-3 py-3 text-left">Duration</th>
          {/if}
        </tr>
      </thead>
      <tbody>
        {#each visibleMatches as m (m.id)}
          <tr
            class={rowClass(m.id)}
            onclick={() => !compact && selectMatch(m.id)}
            class:cursor-default={compact}
          >
            {#if !compact}
              <td class="px-3 py-2.5 text-game-muted">{timeAgo(m.started_at)}</td>
            {/if}
            <td class="px-3 py-2.5">
              <span class="inline-flex items-center gap-2 font-medium text-game-primary">
                <span
                  class="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-game-muted text-xs text-game-muted"
                  aria-hidden="true"
                  >⌖</span
                >
                {mapDisplay(m.map_name)}
              </span>
            </td>
            <td class="px-3 py-2.5 font-medium text-game-primary">
              <span class={m.result === 'win' ? 'text-emerald-700' : 'text-red-600'}>{m.score_team ?? '-'}</span>
              <span class="mx-1 text-game-muted/50">:</span>
              <span class="text-game-muted">{m.score_opponent ?? '-'}</span>
            </td>
            <td class="px-3 py-2.5">
              {#if m.result === 'win'}
                <span class={resultClass(m.result)}>Win</span>
              {:else if m.result === 'loss'}
                <span class={resultClass(m.result)}>Loss</span>
              {:else}
                <span class="text-game-muted">—</span>
              {/if}
            </td>
            {#if !compact}
              <td class="px-3 py-2.5 text-game-muted">
                {m.duration_seconds ? `${Math.round(m.duration_seconds / 60)}m` : '-'}
              </td>
            {/if}
          </tr>
        {/each}
      </tbody>
    </table>
  </div>

  {#if selectedId && !compact}
    <!-- Tab switcher -->
    <div class="mb-4 mt-6 flex gap-1 border-b border-game">
      <button
        class={tab === 'scoreboard'
          ? 'border-b-2 border-[var(--accent)] px-4 py-2 text-sm font-semibold text-game-accent'
          : 'px-4 py-2 text-sm text-game-muted transition-colors hover:text-game-primary'}
        onclick={() => switchTab('scoreboard')}
      >Scoreboard</button>
      <button
        class={tab === 'rounds'
          ? 'border-b-2 border-[var(--accent)] px-4 py-2 text-sm font-semibold text-game-accent'
          : 'px-4 py-2 text-sm text-game-muted transition-colors hover:text-game-primary'}
        onclick={() => switchTab('rounds')}
      >Round breakdown</button>
    </div>

    {#if tab === 'scoreboard'}
      <Scoreboard data={scoreboard} loading={scoreboardLoading} />
    {:else}
      {#if roundsLoading}
        <p class="text-sm text-game-muted">Loading rounds…</p>
      {:else if rounds.length === 0}
        <p class="text-sm text-game-muted">No round data for this match.</p>
      {:else}
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr class="border-b border-game text-xs font-medium uppercase tracking-wider text-game-muted">
                <th class="text-left py-2 px-2">#</th>
                <th class="text-left py-2 px-2">Result</th>
                <th class="text-left py-2 px-2">K</th>
                <th class="text-left py-2 px-2">D</th>
                <th class="text-left py-2 px-2">Weapon</th>
                <th class="text-left py-2 px-2">Accuracy</th>
              </tr>
            </thead>
            <tbody>
              {#each rounds as r (r.id)}
                <tr class="border-b border-game">
                  <td class="px-2 py-1.5 text-game-muted">{r.round_number}</td>
                  <td class="py-1.5 px-2">
                    <span class={roundResultClass(r.winning_team)}>
                      {resultLabel(r.winning_team)}
                    </span>
                  </td>
                  <td class={killClass(r.kills)}>{r.kills ?? 0}</td>
                  <td class={deathClass(r.deaths)}>{r.deaths ?? 0}</td>
                  <td class="px-2 py-1.5 text-game-primary">{r.weapon_used ?? '-'}</td>
                  <td class="px-2 py-1.5 text-xs text-game-muted">
                    {#each r.weapon_stats as ws}
                      <span class="mr-2">
                        {ws.hits}/{ws.shots}
                        <span class="ml-1">
                          ({Math.round((ws.hits / Math.max(1, ws.shots || 1)) * 100)}% acc
                          {#if ws.headshots > 0}
                            , <span class="text-game-accent">{ws.headshots} HS</span>
                          {/if}
                          )
                        </span>
                      </span>
                    {/each}
                  </td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      {/if}
    {/if}
  {/if}
{/if}
