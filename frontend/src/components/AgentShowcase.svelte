<script lang="ts">
  import { agentRole, roleColor } from '../lib/valorant';

  type AgentRow = {
    name: string;
    games: number;
    wins: number;
    kd: number;
    win_rate: number;
  };

  let { agents = [], loading = false }: { agents?: AgentRow[]; loading?: boolean } = $props();

  const hasData = $derived(agents.length > 0);

  // Explicit "no data yet" preview — visibly a sample, never posing as real stats.
  const placeholder: AgentRow[] = [
    { name: 'Jett', games: 0, wins: 0, kd: 0, win_rate: 0 },
    { name: 'Sova', games: 0, wins: 0, kd: 0, win_rate: 0 },
    { name: 'Killjoy', games: 0, wins: 0, kd: 0, win_rate: 0 },
  ];

  const rows = $derived(hasData ? agents.slice(0, 3) : placeholder);
</script>

<div class="grid gap-4 sm:grid-cols-3">
  {#each rows as a, i (a.name + i)}
    {@const role = agentRole(a.name)}
    {@const color = roleColor(role)}
    <div
      class="group relative overflow-hidden border border-game bg-game-card p-5 transition-all duration-300"
      class:opacity-60={!hasData}
      style={`border-radius: var(--radius-card); --chip-color: ${color};`}
    >
      <!-- Role-tinted top accent + hover glow -->
      <div class="absolute inset-x-0 top-0 h-[3px]" style={`background: linear-gradient(90deg, ${color}, transparent 80%);`}></div>
      {#if hasData}
        <div
          class="pointer-events-none absolute -right-8 -top-8 h-28 w-28 rounded-full opacity-30 blur-2xl transition-opacity duration-300 group-hover:opacity-60"
          style={`background: ${color};`}
        ></div>
      {/if}

      <div class="relative flex items-start justify-between gap-2">
        <div class="min-w-0">
          <p class="font-display text-lg font-semibold text-game-primary">{a.name}</p>
          <p class="mt-0.5 text-xs font-medium text-game-muted">
            {#if hasData}
              {a.games} game{a.games === 1 ? '' : 's'}
              {#if a.wins > 0}· {a.wins}W{/if}
            {:else}
              {loading ? 'Loading…' : 'Awaiting matches'}
            {/if}
          </p>
        </div>
        <span class="val-chip shrink-0">{role ?? 'Agent'}</span>
      </div>

      <div class="relative mt-4 flex justify-between gap-4 border-t border-game pt-4 text-sm">
        <div>
          <span class="block text-[0.65rem] uppercase tracking-wider text-game-muted">Win rate</span>
          <span class="font-mono font-bold text-atk">{hasData ? `${a.win_rate.toFixed(0)}%` : '—'}</span>
        </div>
        <div class="text-right">
          <span class="block text-[0.65rem] uppercase tracking-wider text-game-muted">K/D</span>
          <span class="font-mono font-bold text-def">{hasData ? a.kd.toFixed(2) : '—'}</span>
        </div>
      </div>
    </div>
  {/each}
</div>

{#if !hasData}
  <p class="mt-3 text-center text-[0.7rem] text-game-muted">
    {loading
      ? 'Loading agent stats…'
      : 'Preview agents — your real top three fill in once match data loads.'}
  </p>
{/if}
