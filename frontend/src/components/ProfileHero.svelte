<script lang="ts">
  import { onMount } from 'svelte';
  import LiveStatus from './LiveStatus.svelte';

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
  };

  let profile: Profile | null = $state(null);

  onMount(async () => {
    try {
      const res = await fetch(`${apiUrl}/me/`);
      if (res.ok) profile = await res.json();
    } catch { /* backend offline, use defaults */ }
  });

  function fmt(n: number): string {
    return n.toLocaleString();
  }
</script>

<section id="overview" class="min-h-screen flex items-center pt-24 pb-16">
  <div class="max-w-6xl mx-auto px-5 w-full">
    <div class="flex flex-col lg:flex-row items-center gap-12">
      <div class="relative reveal">
        <!-- Double border: outer = Premier, inner = FACEIT -->
        <div
          class="w-44 h-44 md:w-52 md:h-52 rounded-full p-1 shrink-0"
          style="background: {profile?.premier_color_hex ?? 'var(--color-primary-500)'};"
        >
          <div
            class="w-full h-full rounded-full p-1.5"
            style="background: {profile?.faceit_color_hex ?? 'var(--color-primary-500)'};"
          >
            <img
              src={profile?.avatar_url ?? 'https://avatars.steamstatic.com/fef49e7fa7e1997310d705b2a6158ff8dc1cdfeb_full.jpg'}
              alt="pmec"
              class="w-full h-full rounded-full object-cover animate-glow"
            />
          </div>
        </div>
        {#if profile?.faceit_level != null}
          <div
            class="absolute -bottom-2 left-1/2 -translate-x-1/2 text-white text-xs font-bold px-3 py-1 rounded-full shadow-lg border border-white/20"
            style="background-color: {profile.faceit_color_hex ?? 'var(--color-primary-600)'};"
          >
            LVL {profile.faceit_level}
          </div>
        {:else}
          <div class="absolute -bottom-2 left-1/2 -translate-x-1/2 bg-primary-600 text-white text-xs font-bold px-3 py-1 rounded-full shadow-lg">
            LVL 10
          </div>
        {/if}
      </div>

      <div class="text-center lg:text-left reveal stagger-1">
        <h1 class="text-5xl md:text-6xl font-extrabold text-gradient mb-3">pmec</h1>
        <div class="mb-4">
          <LiveStatus apiUrl={apiUrl} />
        </div>

        {#if profile && !profile.api_configured}
          <div class="mb-4 px-4 py-2 rounded-lg border border-amber-500 border-opacity-30 text-sm" style="background: rgba(245,158,11,0.08);">
            <span class="text-amber-400 font-semibold">FACEIT API key not configured</span>
            <span class="text-zinc-500"> — Add your key to <code class="text-zinc-400">backend/.env</code> then click Sync to pull real matches</span>
          </div>
        {/if}

        <div class="flex flex-wrap gap-3 justify-center lg:justify-start">
          {#if profile?.premier_rating != null && profile?.premier_color_hex}
            <span
              class="px-4 py-1.5 rounded-full text-sm font-semibold border border-white/20 text-white"
              style="background-color: {profile.premier_color_hex};"
            >
              Premier {profile.premier_rating.toLocaleString()}
            </span>
          {:else}
            <span class="px-4 py-1.5 rounded-full text-sm font-semibold border border-amber-500 border-opacity-30 text-amber-400" style="background: rgba(245,158,11,0.1);">
              {profile?.rank ?? 'Global Sentinel'}
            </span>
          {/if}
          {#if profile?.faceit_color_hex}
            <span
              class="px-4 py-1.5 rounded-full text-sm font-semibold border border-white/20 text-white"
              style="background-color: {profile.faceit_color_hex};"
            >
              ELO {profile?.elo ?? 2616}
            </span>
          {:else}
            <span class="px-4 py-1.5 rounded-full text-sm font-semibold border border-primary-500 border-opacity-30 text-primary-400" style="background: rgba(124,58,237,0.1);">
              ELO {profile?.elo ?? 2616}
            </span>
          {/if}
          <span class="px-4 py-1.5 rounded-full text-sm font-semibold border border-white border-opacity-10 text-zinc-300" style="background: rgba(255,255,255,0.03);">
            {fmt(profile?.total_hours ?? 9620)}h played
          </span>
          <span class="px-4 py-1.5 rounded-full text-sm font-semibold border border-white border-opacity-10 text-zinc-300" style="background: rgba(255,255,255,0.03);">
            {fmt(profile?.total_matches ?? 0)} matches
          </span>
        </div>
      </div>

      <div class="flex-1 w-full lg:w-auto reveal stagger-2">
        <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div class="stat-card">
            <span class="text-xl md:text-2xl font-extrabold text-cs-green">
              {profile ? profile.win_rate.toFixed(1) : '--'}%
            </span>
            <span class="text-xs uppercase tracking-wider text-zinc-500">Win Rate</span>
          </div>
          <div class="stat-card">
            <span class="text-xl md:text-2xl font-extrabold">
              {profile ? profile.overall_kd.toFixed(2) : '--'}
            </span>
            <span class="text-xs uppercase tracking-wider text-zinc-500">K/D</span>
          </div>
          <div class="stat-card">
            <span class="text-xl md:text-2xl font-extrabold text-amber-400">
              {profile ? profile.headshot_pct.toFixed(1) : '--'}%
            </span>
            <span class="text-xs uppercase tracking-wider text-zinc-500">HS %</span>
          </div>
          <div class="stat-card">
            <span class="text-xl md:text-2xl font-extrabold">
              {fmt(profile?.total_wins ?? 0)}
            </span>
            <span class="text-xs uppercase tracking-wider text-zinc-500">Wins</span>
          </div>
        </div>

        {#if profile?.favorite_map || profile?.favorite_weapon}
          <div class="grid grid-cols-2 gap-3 mt-3">
            {#if profile?.favorite_map}
              <div class="stat-card">
                <span class="text-lg font-bold text-primary-400">{profile.favorite_map}</span>
                <span class="text-xs uppercase tracking-wider text-zinc-500">Top Map</span>
              </div>
            {/if}
            {#if profile?.favorite_weapon}
              <div class="stat-card">
                <span class="text-lg font-bold text-primary-400">{profile.favorite_weapon}</span>
                <span class="text-xs uppercase tracking-wider text-zinc-500">Top Weapon</span>
              </div>
            {/if}
          </div>
        {/if}
      </div>
    </div>
  </div>
</section>
