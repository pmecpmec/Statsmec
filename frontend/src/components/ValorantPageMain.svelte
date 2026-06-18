<script lang="ts">
  import { onMount } from 'svelte';
  import GameSwitcher from './GameSwitcher.svelte';
  import AgentShowcase from './AgentShowcase.svelte';
  import { showDevSetupHints } from '../lib/devHints';
  import { agentRole, roleColor, queueLabel } from '../lib/valorant';

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
    queue: string | null;
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
      kills: number;
      deaths: number;
      assists: number;
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
  const matches = $derived(stats?.matches ?? []);

  // Honest derived labels — everything below maps real API fields, no fabrication.
  const topAgent = $derived(summary?.top_agents?.[0] ?? null);
  const mainRole = $derived(agentRole(topAgent?.name));
  const latestMode = $derived(queueLabel(matches[0]?.queue));
  const hasStats = $derived((summary?.matches ?? 0) > 0);

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
    class="val-scan relative mx-auto max-w-4xl overflow-hidden border border-game bg-game-card px-6 py-12 md:px-14 md:py-14"
    style="border-radius: var(--radius-hero); box-shadow: 0 0 60px rgba(255, 70, 85, 0.08);"
  >
    <!-- ATK vs DEF top split rail -->
    <div class="absolute inset-x-0 top-0 flex h-[3px]" aria-hidden="true">
      <span class="h-full flex-1" style="background: linear-gradient(90deg, var(--atk-bright), transparent);"></span>
      <span class="h-full flex-1" style="background: linear-gradient(90deg, transparent, var(--def-bright));"></span>
    </div>

    <div class="pointer-events-none absolute inset-0 opacity-[0.12]" aria-hidden="true">
      <div
        class="absolute -right-20 -top-20 h-64 w-64 rounded-full blur-3xl"
        style="background: var(--atk);"
      ></div>
      <div
        class="absolute -bottom-16 -left-16 h-56 w-56 rounded-full blur-3xl"
        style="background: var(--def);"
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

      <span class="section-kicker reveal">Agent dossier</span>

      <div class="relative reveal">
        <div
          class="animate-glow rounded-full p-1"
          style="background: linear-gradient(135deg, var(--atk), var(--accent-3) 55%, var(--def)); box-shadow: var(--avatar-glow);"
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
        <!-- Honest badge: the player's main role from real top-agent data, or a
             neutral marker until matches load (no fake rank tier). -->
        <div
          class="absolute -bottom-1 left-1/2 flex -translate-x-1/2 items-center"
          style="border-radius: var(--radius-card);"
        >
          {#if mainRole}
            <span class="val-chip" style={`--chip-color: ${roleColor(mainRole)}; background: var(--bg-secondary); box-shadow: 0 0 20px color-mix(in srgb, ${roleColor(mainRole)} 35%, transparent);`}>
              {mainRole}
            </span>
          {:else}
            <span
              class="border border-[var(--accent)]/40 bg-game-secondary px-3 py-1 font-mono text-[0.6rem] font-bold uppercase tracking-[0.18em] text-game-muted"
              style="border-radius: 9999px;"
            >
              Unranked
            </span>
          {/if}
        </div>
      </div>

      <div class="reveal stagger-1 flex max-w-lg flex-col items-center gap-4">
        <h1 class="font-display text-4xl font-semibold tracking-tight text-gradient md:text-5xl">
          {riotId ?? profile?.nickname ?? 'pmec'}
        </h1>

        <!-- Identity chips: real queue mode + real W/L record -->
        <div class="flex flex-wrap items-center justify-center gap-2">
          {#if latestMode}
            <span class="val-chip" style="--chip-color: var(--atk);">{latestMode}</span>
          {/if}
          {#if topAgent}
            <span class="val-chip" style={`--chip-color: ${roleColor(mainRole)};`}>
              Main · {topAgent.name}
            </span>
          {/if}
          {#if hasStats && summary}
            <span class="val-chip" style="--chip-color: var(--def);">
              {summary.wins}W–{summary.losses}L
            </span>
          {/if}
        </div>

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
          <div
            class="stat-card !items-start border-[var(--atk)]/25 text-left !shadow-[0_0_24px_rgba(255,70,85,0.12)]"
          >
            <span class="hud-label">ACS</span>
            <span class="font-mono text-2xl font-bold text-atk md:text-3xl">
              {statsLoading ? '…' : fmt(summary?.acs)}
            </span>
          </div>
          <div class="stat-card !items-start text-left">
            <span class="hud-label">K/D</span>
            <span class="font-mono text-2xl font-bold text-game-primary md:text-3xl">
              {statsLoading ? '…' : fmt(summary?.kd, 2)}
            </span>
          </div>
          <div
            class="stat-card !items-start border-[var(--def)]/25 text-left !shadow-[0_0_24px_rgba(42,212,200,0.12)]"
          >
            <span class="hud-label">Win%</span>
            <span class="font-mono text-2xl font-bold text-def md:text-3xl">
              {statsLoading ? '…' : summary?.win_rate != null ? `${fmt(summary.win_rate, 0)}%` : '—'}
            </span>
          </div>
        </div>
        {#if hasStats && summary}
          <p class="text-[0.7rem] text-game-muted">
            Based on last {summary.matches} match{summary.matches === 1 ? '' : 'es'} ·
            {summary.kills}/{summary.deaths}/{summary.assists} K/D/A
          </p>
        {/if}

        <GameSwitcher current="valorant" />
      </div>
    </div>
  </div>
</section>

<section id="dashboard" class="bg-game-primary px-4 py-10 md:px-8">
  <div class="mx-auto max-w-7xl">
    <div class="reveal mb-7 flex flex-col items-center text-center">
      <span class="section-kicker mb-2">Top agents</span>
      <h2 class="section-title-accent font-display text-2xl font-semibold text-game-primary md:text-3xl">
        Agent performance
      </h2>
    </div>
    <AgentShowcase agents={summary?.top_agents ?? []} loading={statsLoading && !stats} />

    <div class="mt-8 grid gap-6 lg:grid-cols-5">
      <!-- Combat record — real summary numbers only -->
      <div class="glass-card val-rail reveal pl-7 lg:col-span-2" style="--rail-color: var(--atk);">
        <h3 class="section-title-accent mb-5 font-display text-lg font-semibold text-game-primary">
          Combat record
        </h3>
        {#if statsLoading && !stats}
          <p class="text-sm text-game-muted">Loading…</p>
        {:else if hasStats && summary}
          <div class="space-y-5">
            <div class="grid grid-cols-3 gap-2 text-center">
              <div>
                <span class="hud-label">Kills</span>
                <span class="mt-1 block font-mono text-xl font-bold text-atk">{summary.kills}</span>
              </div>
              <div>
                <span class="hud-label">Deaths</span>
                <span class="mt-1 block font-mono text-xl font-bold text-def">{summary.deaths}</span>
              </div>
              <div>
                <span class="hud-label">Assists</span>
                <span class="mt-1 block font-mono text-xl font-bold text-game-secondary">{summary.assists}</span>
              </div>
            </div>

            <!-- Win / loss split bar (ATK wins vs DEF losses) -->
            <div>
              <div class="mb-1.5 flex items-center justify-between">
                <span class="hud-label">Win rate</span>
                <span class="font-mono text-xs font-semibold text-game-primary">{fmt(summary.win_rate, 0)}%</span>
              </div>
              <div class="flex h-2.5 w-full overflow-hidden rounded-full bg-game-secondary">
                <div
                  class="h-full"
                  style={`width:${summary.matches ? (summary.wins / summary.matches) * 100 : 0}%; background: linear-gradient(90deg, var(--atk-bright), var(--atk));`}
                ></div>
                <div
                  class="h-full flex-1"
                  style="background: linear-gradient(90deg, var(--def), var(--def-bright));"
                ></div>
              </div>
              <div class="mt-1.5 flex justify-between font-mono text-[0.65rem]">
                <span class="text-atk">{summary.wins}W</span>
                <span class="text-def">{summary.losses}L</span>
              </div>
            </div>

            <div class="grid grid-cols-2 gap-3 border-t border-game pt-4">
              <div>
                <span class="hud-label">Avg ACS</span>
                <span class="mt-1 block font-mono text-lg font-bold text-game-primary">{summary.acs}</span>
              </div>
              <div>
                <span class="hud-label">K/D ratio</span>
                <span class="mt-1 block font-mono text-lg font-bold text-game-primary">{fmt(summary.kd, 2)}</span>
              </div>
            </div>
          </div>
        {:else}
          <p class="text-sm text-game-muted">No aggregated combat data for this account yet.</p>
        {/if}
      </div>

      <!-- Recent matches -->
      <div class="glass-card reveal stagger-1 lg:col-span-3" id="matches">
        <h3 class="section-title-accent mb-5 font-display text-lg font-semibold text-game-primary">Recent matches</h3>
        <p class="mb-4 text-sm text-game-muted">
          Last matches for <strong class="text-game-primary">{riotId ?? 'selected account'}</strong>.
        </p>
        {#if statsLoading || !val}
          <p class="text-sm text-game-muted">Loading…</p>
        {:else if matches.length > 0}
          <ul class="space-y-2 text-sm">
            {#each matches as m (m.match_id ?? m.started_at)}
              {@const role = agentRole(m.agent)}
              <li
                class="val-rail flex items-center justify-between gap-3 border border-game bg-game-muted px-3 py-2.5 pl-5 transition-colors hover:border-[var(--accent)]/25"
                style={`border-radius: calc(var(--radius-card) - 2px); --rail-color: ${m.won ? 'var(--atk)' : 'var(--def)'};`}
              >
                <div class="flex min-w-0 flex-col">
                  <span class="font-display font-semibold text-game-primary">{m.map}</span>
                  <span class="flex items-center gap-1.5 text-[0.7rem]">
                    <span class="font-medium" style={`color: ${roleColor(role)};`}>{m.agent}</span>
                    {#if role}<span class="text-game-muted">· {role}</span>{/if}
                  </span>
                </div>
                <div class="flex items-center gap-3 font-mono text-xs md:gap-4">
                  <span class="hidden text-game-secondary sm:inline">{m.kills}/{m.deaths}/{m.assists}</span>
                  <span class="text-game-accent-2">{m.acs} ACS</span>
                  <span
                    class="min-w-[3rem] rounded px-2 py-1 text-right font-bold"
                    style={m.won
                      ? 'color: var(--atk-bright); background: var(--atk-soft);'
                      : 'color: var(--def-bright); background: var(--def-soft);'}
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
  </div>
</section>
