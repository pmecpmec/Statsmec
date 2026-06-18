<script lang="ts">
  import { onMount } from 'svelte';
  import LiveStatus from './LiveStatus.svelte';
  import GameSwitcher from './GameSwitcher.svelte';
  import { showDevSetupHints } from '../lib/devHints';

  let { apiUrl = 'http://127.0.0.1:8000/api/v1' } = $props();

  type Profile = {
    nickname: string;
    steam_id: string;
    faceit_nickname: string;
    avatar_url: string;
    rank: string;
    elo: number;
    total_matches: number;
    total_wins: number;
    total_losses: number;
    win_rate: number;
    overall_kd: number;
    headshot_pct: number;
    total_hours: number;
    favorite_map: string | null;
    favorite_weapon: string | null;
    api_configured: boolean;
    faceit_level?: number | null;
    faceit_color_hex?: string | null;
    premier_rating?: number | null;
    premier_color_hex?: string | null;
    riot_api_configured?: boolean;
  };

  let profile: Profile | null = $state(null);

  onMount(async () => {
    try {
      const res = await fetch(`${apiUrl}/me/`);
      if (res.ok) profile = await res.json();
    } catch {
      /* backend offline */
    }
  });

  function fmt(n: number): string {
    return n.toLocaleString();
  }

  const displayName = $derived(profile?.faceit_nickname || profile?.nickname || 'pmec');
</script>

<section id="overview" class="px-4 pb-8 pt-6 md:px-8 md:pb-10 md:pt-8">
  <div
    class="relative mx-auto max-w-4xl overflow-hidden border border-game bg-game-card px-6 py-10 md:px-12 md:py-12"
    style="border-radius: var(--radius-hero);"
  >
    <div class="hero-waves" aria-hidden="true">
      <svg viewBox="0 0 1440 320" fill="none" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none">
        <path
          opacity="0.35"
          d="M0 160C240 80 480 240 720 200C960 160 1200 40 1440 100V320H0V160Z"
          fill="currentColor"
        />
      </svg>
    </div>

    <div class="relative flex flex-col items-center gap-8">
      <div class="relative reveal">
        <div class="animate-glow rounded-full p-[3px]" style="background: var(--accent); box-shadow: var(--avatar-glow, none);">
          <div class="rounded-full bg-game-card p-[3px]">
            <img
              src={profile?.avatar_url ??
                'https://avatars.steamstatic.com/fef49e7fa7e1997310d705b2a6158ff8dc1cdfeb_full.jpg'}
              alt={displayName}
              class="h-28 w-28 rounded-full object-cover md:h-36 md:w-36"
            />
          </div>
        </div>
        <div
          class="absolute -bottom-1 left-1/2 flex -translate-x-1/2 flex-col items-center border border-game bg-game-secondary px-3 py-1 text-center"
          style="border-radius: calc(var(--radius-card) - 2px);"
        >
          <span class="text-lg font-bold leading-none text-game-accent">
            {profile?.faceit_level ?? 10}
          </span>
          <span class="text-[0.65rem] font-medium uppercase tracking-wider text-game-muted">FACEIT</span>
        </div>
      </div>

      <div class="reveal stagger-1 flex w-full max-w-xl flex-col items-center gap-5 text-center">
        <h1 class="font-display text-3xl font-semibold tracking-tight text-game-primary md:text-4xl">
          {displayName}
        </h1>
        <LiveStatus
          apiUrl={apiUrl}
          faceitSyncVisible={showDevSetupHints || profile?.api_configured === true}
        />

        {#if profile && !profile.api_configured && showDevSetupHints}
          <div
            class="w-full border border-game bg-game-muted px-4 py-3 text-left text-sm text-game-secondary"
            style="border-radius: var(--radius-card);"
          >
            <span class="font-semibold text-game-accent">FACEIT API key not configured</span>
            <span class="text-game-muted">
              — Add <code class="rounded bg-game-card px-1 font-mono text-xs">FACEIT_API_KEY</code> to backend env, then sync.</span
            >
          </div>
        {/if}

        {#if profile?.riot_api_configured && showDevSetupHints}
          <p class="text-center text-xs text-game-muted">
            Riot API ready — use the <a href="/valorant" class="text-game-accent underline hover:no-underline">Valorant</a> page
            or set <code class="font-mono">RIOT_GAME_NAME</code> / <code class="font-mono">RIOT_TAG_LINE</code>.
          </p>
        {/if}

        <div class="flex flex-wrap items-center justify-center gap-2">
          {#if profile?.premier_rating != null && profile?.premier_color_hex}
            <span
              class="border border-game px-3 py-1 text-xs font-semibold text-white"
              style="border-radius: var(--radius-card); background-color: {profile.premier_color_hex};"
            >
              Premier {profile.premier_rating.toLocaleString()}
            </span>
          {:else}
            <span
              class="border border-game bg-game-muted px-3 py-1 text-xs font-semibold text-game-primary"
              style="border-radius: var(--radius-card);"
            >
              {profile?.rank ?? 'Premier'}
            </span>
          {/if}
          {#if profile?.faceit_color_hex}
            <span
              class="border border-game px-3 py-1 text-xs font-semibold text-white"
              style="border-radius: var(--radius-card); background-color: {profile.faceit_color_hex};"
            >
              ELO {profile?.elo ?? '—'}
            </span>
          {:else}
            <span
              class="border border-[var(--accent)]/30 bg-[var(--accent-soft)] px-3 py-1 text-xs font-semibold text-game-accent"
              style="border-radius: var(--radius-card);"
            >
              ELO {profile?.elo ?? '—'}
            </span>
          {/if}
          <span
            class="border border-game bg-game-muted px-3 py-1 text-xs font-medium text-game-muted"
            style="border-radius: var(--radius-card);"
          >
            {fmt(profile?.total_hours ?? 0)}h
          </span>
          <span
            class="border border-game bg-game-muted px-3 py-1 text-xs font-medium text-game-muted"
            style="border-radius: var(--radius-card);"
          >
            {fmt(profile?.total_matches ?? 0)} matches
          </span>
        </div>

        <div class="grid w-full max-w-md grid-cols-3 gap-2 pt-2 md:gap-3">
          <div class="stat-card">
            <span class="text-[0.65rem] font-semibold uppercase tracking-wider text-game-muted">Win rate</span>
            <span class="font-mono text-xl font-bold text-game-accent md:text-2xl">
              {profile ? `${profile.win_rate.toFixed(1)}%` : '—'}
            </span>
          </div>
          <div class="stat-card">
            <span class="text-[0.65rem] font-semibold uppercase tracking-wider text-game-muted">K/D</span>
            <span class="font-mono text-xl font-bold text-game-primary md:text-2xl">
              {profile ? profile.overall_kd.toFixed(2) : '—'}
            </span>
          </div>
          <div class="stat-card">
            <span class="text-[0.65rem] font-semibold uppercase tracking-wider text-game-muted">HS%</span>
            <span class="font-mono text-xl font-bold text-game-accent md:text-2xl">
              {profile ? `${profile.headshot_pct.toFixed(0)}%` : '—'}
            </span>
          </div>
        </div>

        {#if profile?.favorite_map || profile?.favorite_weapon}
          <div class="grid w-full max-w-lg grid-cols-1 gap-2 sm:grid-cols-2">
            {#if profile?.favorite_map}
              <div class="border border-game bg-game-muted px-4 py-3 text-center" style="border-radius: var(--radius-card);">
                <span class="text-xs font-semibold uppercase tracking-wider text-game-muted">Top map</span>
                <span class="mt-1 block font-display text-lg font-semibold text-game-accent">{profile.favorite_map}</span>
              </div>
            {/if}
            {#if profile?.favorite_weapon}
              <div class="border border-game bg-game-muted px-4 py-3 text-center" style="border-radius: var(--radius-card);">
                <span class="text-xs font-semibold uppercase tracking-wider text-game-muted">Top weapon</span>
                <span class="mt-1 block font-display text-lg font-semibold text-game-accent"
                  >{profile.favorite_weapon}</span
                >
              </div>
            {/if}
          </div>
        {/if}

        <GameSwitcher current="cs2" />
      </div>
    </div>
  </div>
</section>
