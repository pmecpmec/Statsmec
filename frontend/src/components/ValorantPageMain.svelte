<script lang="ts">
  import { onMount } from 'svelte';
  import GameSwitcher from './GameSwitcher.svelte';
  import AgentShowcase from './AgentShowcase.svelte';
  import { showDevSetupHints } from '../lib/devHints';

  let { apiUrl = 'http://127.0.0.1:8000/api/v1' } = $props();

  type AccountRow = {
    game_name: string | null;
    tag_line: string | null;
    puuid: string | null;
    recent_match_ids: string[];
    error: string | null;
  };

  type ValorantPayload = {
    api_configured: boolean;
    accounts: AccountRow[];
    error: string | null;
  };

  type Profile = {
    nickname: string;
    avatar_url: string;
  };

  type AgentRow = {
    name: string;
    games: number;
    wins: number;
    kd: number;
    win_rate: number;
  };

  type MatchRow = {
    match_id: string | null;
    map: string;
    agent: string;
    kills: number;
    deaths: number;
    assists: number;
    acs: number;
    kd: number;
    score: string;
    won: boolean;
    started_at: number | null;
  };

  type StatsPayload = {
    api_configured: boolean;
    game_name: string | null;
    tag_line: string | null;
    summary: {
      matches: number;
      wins: number;
      losses: number;
      win_rate: number;
      kd: number;
      acs: number;
      top_agents: AgentRow[];
    };
    matches: MatchRow[];
    error: string | null;
  };

  let val: ValorantPayload | null = $state(null);
  let profile: Profile | null = $state(null);
  let stats: StatsPayload | null = $state(null);
  let statsLoading = $state(false);
  let selectedIdx = $state(0);

  onMount(async () => {
    try {
      const [vr, pr] = await Promise.all([
        fetch(`${apiUrl}/me/valorant`),
        fetch(`${apiUrl}/me/`),
      ]);
      if (vr.ok) val = await vr.json();
      if (pr.ok) profile = await pr.json();
    } catch {
      /* offline */
    }
  });

  const accounts = $derived(val?.accounts ?? []);
  const active = $derived(accounts[selectedIdx] ?? null);
  const riotId = $derived(
    active?.game_name && active?.tag_line ? `${active.game_name}#${active.tag_line}` : null
  );
  const summary = $derived(stats?.summary ?? null);
  const fmt = (v: number | null | undefined, digits = 0) =>
    v === null || v === undefined ? '—' : v.toFixed(digits);

  // Load real per-match stats for the active account; refetch when the selection changes.
  $effect(() => {
    const acc = active;
    if (!acc?.game_name || !acc?.tag_line) {
      stats = null;
      return;
    }
    let cancelled = false;
    statsLoading = true;
    const qs = new URLSearchParams({ game_name: acc.game_name, tag_line: acc.tag_line });
    fetch(`${apiUrl}/me/valorant/stats?${qs}`)
      .then((r) => (r.ok ? r.json() : null))
      .then((data) => {
        if (!cancelled) stats = data;
      })
      .catch(() => {
        if (!cancelled) stats = null;
      })
      .finally(() => {
        if (!cancelled) statsLoading = false;
      });
    return () => {
      cancelled = true;
    };
  });

  function selectAccount(i: number) {
    selectedIdx = i;
  }
</script>

<section id="overview" class="px-4 pb-10 pt-6 md:px-8 md:pt-8">
  <div
    class="relative mx-auto max-w-4xl overflow-hidden border border-game bg-game-card px-6 py-12 md:px-14 md:py-14"
    style="border-radius: var(--radius-hero); box-shadow: 0 0 60px rgba(255, 70, 85, 0.08);"
  >
    <div class="pointer-events-none absolute inset-0 opacity-[0.12]" aria-hidden="true">
      <div
        class="absolute -right-20 -top-20 h-64 w-64 rounded-full blur-3xl"
        style="background: var(--accent);"
      ></div>
      <div
        class="absolute -bottom-16 -left-16 h-56 w-56 rounded-full blur-3xl"
        style="background: var(--accent-2);"
      ></div>
      <div
        class="absolute left-1/2 top-1/2 h-48 w-48 -translate-x-1/2 -translate-y-1/2 rounded-full blur-3xl"
        style="background: var(--accent-3);"
      ></div>
    </div>

    <div class="relative flex flex-col items-center gap-8 text-center">
      {#if accounts.length > 1}
        <div class="flex flex-wrap items-center justify-center gap-2" role="tablist" aria-label="Valorant accounts">
          {#each accounts as acc, i (i)}
            <button
              type="button"
              role="tab"
              aria-selected={selectedIdx === i}
              class="border px-4 py-2 text-sm font-semibold transition-all"
              style="border-radius: var(--radius-card);"
              class:border-[var(--accent)]={selectedIdx === i}
              class:bg-[var(--accent-soft)]={selectedIdx === i}
              class:text-game-primary={selectedIdx === i}
              class:border-game={selectedIdx !== i}
              class:text-game-muted={selectedIdx !== i}
              class:valorant-account-tab-inactive={selectedIdx !== i}
              onclick={() => selectAccount(i)}
            >
              {acc.game_name ?? `Account ${i + 1}`}
            </button>
          {/each}
        </div>
      {/if}

      <div class="relative reveal">
        <div
          class="animate-glow rounded-full p-1"
          style="background: linear-gradient(135deg, var(--accent), var(--accent-3)); box-shadow: var(--avatar-glow);"
        >
          <div class="rounded-full bg-game-card p-1">
            <img
              src={profile?.avatar_url ??
                'https://avatars.steamstatic.com/fef49e7fa7e1997310d705b2a6158ff8dc1cdfeb_full.jpg'}
              alt={riotId ?? 'Agent'}
              class="h-28 w-28 rounded-full object-cover md:h-36 md:w-36"
            />
          </div>
        </div>
        <div
          class="absolute -bottom-1 left-1/2 flex -translate-x-1/2 flex-col items-center border border-[var(--accent)]/40 bg-game-secondary px-4 py-1.5"
          style="border-radius: var(--radius-card); box-shadow: 0 0 20px rgba(255, 70, 85, 0.25);"
        >
          <span class="text-[0.6rem] font-bold uppercase tracking-[0.2em] text-game-accent">Rank</span>
          <span class="font-display text-sm font-semibold text-game-primary">Competitive</span>
        </div>
      </div>

      <div class="reveal stagger-1 flex max-w-lg flex-col items-center gap-4">
        <h1 class="font-display text-4xl font-semibold tracking-tight text-gradient md:text-5xl">
          {riotId ?? profile?.nickname ?? 'pmec'}
        </h1>

        {#if val && !val.api_configured && showDevSetupHints}
          <p class="text-sm text-game-muted">
            Configure <code class="font-mono text-game-accent">RIOT_API_KEY</code> in backend env.
          </p>
        {:else if showDevSetupHints && val?.error && accounts.length === 0}
          <p class="text-sm text-game-muted">{val.error}</p>
        {:else if showDevSetupHints && active?.error}
          <p class="text-sm text-game-muted">{active.error}</p>
        {:else if active?.puuid}
          <p class="text-xs text-game-muted">
            {active.recent_match_ids.length} recent matches (Riot API) for this Riot ID
          </p>
        {/if}

        <div class="grid w-full max-w-lg grid-cols-3 gap-3">
          <div class="stat-card border-[var(--accent)]/20 !shadow-[0_0_24px_rgba(255,70,85,0.12)]">
            <span class="text-[0.65rem] uppercase tracking-wider text-game-muted">ACS</span>
            <span class="font-mono text-xl font-bold text-game-accent-2 md:text-2xl">
              {statsLoading ? '…' : fmt(summary?.acs)}
            </span>
          </div>
          <div class="stat-card border-[var(--accent)]/20 !shadow-[0_0_24px_rgba(255,70,85,0.12)]">
            <span class="text-[0.65rem] uppercase tracking-wider text-game-muted">K/D</span>
            <span class="font-mono text-xl font-bold text-game-primary md:text-2xl">
              {statsLoading ? '…' : fmt(summary?.kd, 2)}
            </span>
          </div>
          <div class="stat-card border-[var(--accent)]/20 !shadow-[0_0_24px_rgba(255,70,85,0.12)]">
            <span class="text-[0.65rem] uppercase tracking-wider text-game-muted">Win%</span>
            <span class="font-mono text-xl font-bold text-game-accent md:text-2xl">
              {statsLoading ? '…' : summary?.win_rate != null ? `${fmt(summary.win_rate, 0)}%` : '—'}
            </span>
          </div>
        </div>
        {#if summary && summary.matches > 0}
          <p class="text-[0.7rem] text-game-muted">
            Based on last {summary.matches} match{summary.matches === 1 ? '' : 'es'} ·
            {summary.wins}W–{summary.losses}L
          </p>
        {/if}

        <GameSwitcher current="valorant" />
      </div>
    </div>
  </div>
</section>

<section id="dashboard" class="bg-game-primary px-4 py-10 md:px-8">
  <div class="mx-auto grid max-w-7xl gap-8 lg:grid-cols-2">
    <div class="glass-card reveal">
      <h2 class="section-title-accent mb-6 font-display text-xl font-semibold text-game-primary">Agent performance</h2>
      <AgentShowcase agents={summary?.top_agents ?? []} />
    </div>
    <div class="glass-card reveal stagger-1" id="matches">
      <h2 class="section-title-accent mb-6 font-display text-xl font-semibold text-game-primary">Recent matches</h2>
      <p class="mb-4 text-sm text-game-muted">
        Last matches for <strong class="text-game-primary">{riotId ?? 'selected account'}</strong>.
      </p>
      {#if statsLoading || !val}
        <p class="text-sm text-game-muted">Loading…</p>
      {:else if stats && stats.matches.length > 0}
        <ul class="space-y-2 text-sm">
          {#each stats.matches as m (m.match_id ?? m.started_at)}
            <li
              class="flex items-center justify-between gap-3 border border-l-2 border-game bg-game-muted px-3 py-2.5"
              style="border-radius: calc(var(--radius-card) - 2px);"
              style:border-left-color={m.won ? 'var(--badge-win-bg)' : 'var(--badge-loss-text)'}
            >
              <div class="flex min-w-0 flex-col">
                <span class="font-display font-semibold text-game-primary">{m.map}</span>
                <span class="text-[0.7rem] text-game-muted">{m.agent}</span>
              </div>
              <div class="flex items-center gap-4 font-mono text-xs">
                <span class="text-game-secondary">{m.kills}/{m.deaths}/{m.assists}</span>
                <span class="text-game-accent-2">{m.acs} ACS</span>
                <span
                  class="w-12 text-right font-semibold"
                  class:text-game-accent={m.won}
                  class:text-game-muted={!m.won}
                >
                  {m.score}
                </span>
              </div>
            </li>
          {/each}
        </ul>
      {:else if stats?.error}
        <p class="text-sm text-game-muted">{stats.error}</p>
      {:else}
        <p class="text-sm text-game-muted">No match data returned for this account yet.</p>
      {/if}
    </div>
  </div>
</section>
