<script lang="ts">
  type AgentRow = {
    name: string;
    games: number;
    wins: number;
    kd: number;
    win_rate: number;
  };

  let { agents = [] }: { agents?: AgentRow[] } = $props();

  // Subtle per-agent glow so cards don't look identical; falls back across the list.
  const ACCENTS = [
    'from-sky-400/30 to-transparent',
    'from-fuchsia-500/25 to-transparent',
    'from-violet-500/30 to-transparent',
  ];

  const hasData = $derived(agents.length > 0);

  // Placeholder shown until real match data is aggregated.
  const placeholder: AgentRow[] = [
    { name: 'Jett', games: 0, wins: 0, kd: 1.35, win_rate: 62 },
    { name: 'Reyna', games: 0, wins: 0, kd: 1.28, win_rate: 58 },
    { name: 'Omen', games: 0, wins: 0, kd: 1.12, win_rate: 55 },
  ];

  const rows = $derived(hasData ? agents.slice(0, 3) : placeholder);
</script>

<div class="grid gap-4 sm:grid-cols-3">
  {#each rows as a, i (a.name)}
    <div
      class="group relative overflow-hidden border border-game bg-game-card p-5 transition-all duration-300 hover:border-[var(--accent)]/35"
      class:opacity-70={!hasData}
      style="border-radius: var(--radius-card); box-shadow: 0 0 0 transparent;"
    >
      <div
        class="pointer-events-none absolute inset-0 opacity-0 transition-opacity duration-300 group-hover:opacity-100"
        style="background: radial-gradient(circle at 80% 20%, var(--glow-accent), transparent 55%);"
      ></div>
      <div
        class="absolute -right-6 top-0 h-32 w-32 rounded-full bg-gradient-to-br opacity-40 blur-2xl {ACCENTS[i % ACCENTS.length]}"
      ></div>
      <p class="font-display text-lg font-semibold text-game-primary">{a.name}</p>
      <p class="text-xs font-medium uppercase tracking-wider text-game-accent">
        {hasData ? `${a.games} game${a.games === 1 ? '' : 's'}` : 'Sample'}
      </p>
      <div class="mt-4 flex justify-between gap-4 border-t border-game pt-4 text-sm">
        <div>
          <span class="block text-[0.65rem] uppercase text-game-muted">Win rate</span>
          <span class="font-mono font-bold text-game-accent">{a.win_rate.toFixed(0)}%</span>
        </div>
        <div>
          <span class="block text-[0.65rem] uppercase text-game-muted">K/D</span>
          <span class="font-mono font-bold text-game-accent-2">{a.kd.toFixed(2)}</span>
        </div>
      </div>
    </div>
  {/each}
</div>

{#if !hasData}
  <p class="mt-3 text-center text-[0.7rem] text-game-muted">Sample data — fills in once matches load.</p>
{/if}
