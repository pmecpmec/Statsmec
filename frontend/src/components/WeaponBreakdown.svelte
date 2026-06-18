<script lang="ts">
  import { onMount, tick } from 'svelte';

  let { apiUrl = 'http://127.0.0.1:8000/api/v1' } = $props();

  type WeaponAgg = { weapon: string; accuracy: number };
  let weapons: WeaponAgg[] = $state([]);
  let error = $state('');
  let canvas: HTMLCanvasElement | undefined = $state(undefined);
  let tab: 'grid' | 'chart' = $state('grid');

  let chartInstance: { destroy: () => void } | null = null;

  onMount(async () => {
    try {
      const res = await fetch(`${apiUrl}/analytics/users/1`);
      const json = await res.json();
      const heatmaps = json.weapon_heatmaps ?? {};
      weapons = Object.entries(heatmaps)
        .map(([weapon, maps]: [string, unknown]) => {
          const list = Array.isArray(maps) ? maps : [];
          const cells = (list as { cells?: { intensity: number }[] }[]).flatMap((m) => m.cells ?? []);
          const avg = cells.length ? cells.reduce((s, c) => s + c.intensity, 0) / cells.length : 0;
          return { weapon, accuracy: Math.round(avg * 100) };
        })
        .sort((a, b) => b.accuracy - a.accuracy)
        .slice(0, 9);
    } catch {
      error = 'Could not load weapon data.';
    }
  });

  function chartTheme() {
    if (typeof document === 'undefined') {
      return {
        tipBg: '#121821',
        tipBorder: 'rgba(255,255,255,0.08)',
        tipTitle: '#e6edf3',
        tipBody: '#9aa7b2',
        tick: '#9aa7b2',
        grid: 'rgba(230,237,243,0.06)',
        yTick: '#9aa7b2',
      };
    }
    const s = getComputedStyle(document.documentElement);
    return {
      tipBg: s.getPropertyValue('--bg-card').trim() || '#121821',
      tipBorder: 'rgba(255,255,255,0.08)',
      tipTitle: s.getPropertyValue('--text-primary').trim() || '#e6edf3',
      tipBody: s.getPropertyValue('--text-secondary').trim() || '#9aa7b2',
      tick: s.getPropertyValue('--text-muted').trim() || '#5c6b7a',
      grid: 'rgba(255,255,255,0.06)',
      yTick: s.getPropertyValue('--text-secondary').trim() || '#9aa7b2',
    };
  }

  async function drawChart() {
    if (!canvas || !weapons.length) return;
    if (chartInstance) {
      chartInstance.destroy();
      chartInstance = null;
    }
    const { Chart, registerables } = await import('chart.js');
    Chart.register(...registerables);

    const t = chartTheme();
    const s = getComputedStyle(document.documentElement);
    const line = s.getPropertyValue('--accent').trim() || '#f2a900';
    const ct = s.getPropertyValue('--ct-bright').trim() || '#7cc0f5';
    const tt = s.getPropertyValue('--t-bright').trim() || '#f4c94b';
    const barColors = weapons.map((_, i) => {
      const hues = [line, ct, tt, '#94a3b8'];
      return hues[i % hues.length];
    });

    chartInstance = new Chart(canvas, {
      type: 'bar',
      data: {
        labels: weapons.map((w) => w.weapon),
        datasets: [
          {
            label: 'Accuracy %',
            data: weapons.map((w) => w.accuracy),
            backgroundColor: barColors,
            borderRadius: 6,
            barThickness: 22,
          },
        ],
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: t.tipBg,
            borderColor: t.tipBorder,
            borderWidth: 1,
            titleColor: t.tipTitle,
            bodyColor: t.tipBody,
            callbacks: { label: (ctx: { parsed: { x: number } }) => `${ctx.parsed.x}%` },
          },
        },
        scales: {
          x: {
            ticks: {
              color: t.tick,
              font: { size: 10 },
              callback: (v: string | number) => `${v}%`,
            },
            grid: { color: t.grid },
          },
          y: {
            ticks: { color: t.yTick, font: { size: 11 } },
            grid: { display: false },
          },
        },
      },
    });
  }

  async function selectTab(next: 'grid' | 'chart') {
    tab = next;
    if (next === 'chart') {
      await tick();
      await drawChart();
    } else if (chartInstance) {
      chartInstance.destroy();
      chartInstance = null;
    }
  }
</script>

<div class="mb-4 flex flex-wrap items-center justify-between gap-3 border-b border-game pb-3">
  <h3 class="font-display text-lg font-semibold text-game-primary">Weapon breakdown</h3>
  <div class="flex gap-4 text-sm font-medium">
    <button
      type="button"
      class="border-b-2 pb-1 transition-colors"
      class:border-[var(--accent)]={tab === 'grid'}
      class:text-game-accent={tab === 'grid'}
      class:border-transparent={tab !== 'grid'}
      class:text-game-muted={tab !== 'grid'}
      onclick={() => selectTab('grid')}
    >
      CS2
    </button>
    <button
      type="button"
      class="border-b-2 pb-1 transition-colors"
      class:border-[var(--accent)]={tab === 'chart'}
      class:text-game-accent={tab === 'chart'}
      class:border-transparent={tab !== 'chart'}
      class:text-game-muted={tab !== 'chart'}
      onclick={() => selectTab('chart')}
    >
      Chart
    </button>
  </div>
</div>

{#if error}
  <p class="text-sm text-red-600">{error}</p>
{:else if weapons.length === 0}
  <p class="text-sm text-game-muted">No weapon data yet.</p>
{:else if tab === 'grid'}
  <div class="grid grid-cols-2 gap-3 sm:grid-cols-3">
    {#each weapons as w (w.weapon)}
      <div
        class="flex flex-col gap-2 border border-game bg-game-muted/50 p-3 shadow-sm transition-shadow hover:shadow-md"
        style="border-radius: var(--radius-card);"
      >
        <div
          class="mx-auto flex h-14 w-full max-w-[5rem] items-end justify-center rounded-lg bg-gradient-to-b from-[var(--bg-card-muted)] to-[var(--bg-card)]"
          aria-hidden="true"
        >
          <div
            class="mb-1 h-8 w-[70%] rounded-sm bg-game-primary/90"
            style="clip-path: polygon(10% 0, 90% 0, 100% 100%, 0 100%);"
          ></div>
        </div>
        <p class="text-center font-display text-sm font-semibold text-game-primary">{w.weapon}</p>
        <div>
          <div class="flex justify-between gap-2 text-xs text-game-muted">
            <span class="hud-label">Usage</span>
            <span class="font-mono font-semibold text-game-accent">{w.accuracy}%</span>
          </div>
          <div class="mt-1.5 h-1 w-full overflow-hidden rounded-full bg-game-secondary">
            <div
              class="h-full rounded-full"
              style={`width:${Math.max(4, Math.min(100, w.accuracy))}%; background: linear-gradient(90deg, var(--ct-bright), var(--accent), var(--t-bright));`}
            ></div>
          </div>
        </div>
      </div>
    {/each}
  </div>
{:else}
  <div class="h-56">
    <canvas bind:this={canvas}></canvas>
  </div>
{/if}
