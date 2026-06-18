<script lang="ts">
  import { onMount } from 'svelte';

  let { apiUrl = 'http://127.0.0.1:8000/api/v1' } = $props();

  type TrendPoint = { date: string; wins: number; losses: number; matches: number };
  let data: TrendPoint[] = $state([]);
  let error = $state('');
  let canvas: HTMLCanvasElement | undefined = $state(undefined);
  let rangeLabel = $state('Last month');

  onMount(async () => {
    try {
      const res = await fetch(`${apiUrl}/analytics/users/1`);
      const json = await res.json();
      data = (json.win_rate_trend ?? []) as TrendPoint[];
      if (data.length && canvas) drawChart();
    } catch {
      error = 'Could not load trends.';
    }
  });

  function accentColors(): { line: string; fill: string; tick: string; grid: string; tipBg: string; tipTitle: string; tipBody: string } {
    if (typeof document === 'undefined') {
      return {
        line: '#f2a900',
        fill: 'rgba(242, 169, 0, 0.15)',
        tick: '#9aa7b2',
        grid: 'rgba(230, 237, 243, 0.06)',
        tipBg: '#121821',
        tipTitle: '#e6edf3',
        tipBody: '#9aa7b2',
      };
    }
    const s = getComputedStyle(document.documentElement);
    const line = (s.getPropertyValue('--accent').trim() || '#f2a900').replace(/['"]/g, '');
    const game = document.documentElement.dataset.game;
    const isVal = game === 'valorant';
    return {
      line,
      fill: isVal ? 'rgba(255, 70, 85, 0.12)' : 'rgba(242, 169, 0, 0.12)',
      tick: (s.getPropertyValue('--text-muted').trim() || '#5c6b7a').replace(/['"]/g, ''),
      grid: isVal ? 'rgba(255, 255, 255, 0.06)' : 'rgba(230, 237, 243, 0.06)',
      tipBg: (s.getPropertyValue('--bg-card').trim() || '#121821').replace(/['"]/g, ''),
      tipTitle: (s.getPropertyValue('--text-primary').trim() || '#e6edf3').replace(/['"]/g, ''),
      tipBody: (s.getPropertyValue('--text-secondary').trim() || '#9aa7b2').replace(/['"]/g, ''),
    };
  }

  async function drawChart() {
    if (!canvas) return;
    const { Chart, registerables } = await import('chart.js');
    Chart.register(...registerables);

    const c = accentColors();

    new Chart(canvas, {
      type: 'line',
      data: {
        labels: data.map((d) => d.date),
        datasets: [
          {
            label: 'Win rate',
            data: data.map((d) => (d.matches ? Math.round((d.wins / d.matches) * 100) : 0)),
            borderColor: c.line,
            backgroundColor: c.fill,
            fill: true,
            tension: 0.4,
            pointRadius: 3,
            pointBackgroundColor: c.line,
            borderWidth: 2,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: c.tipBg,
            borderColor: 'rgba(255,255,255,0.08)',
            borderWidth: 1,
            titleColor: c.tipTitle,
            bodyColor: c.tipBody,
            callbacks: { label: (ctx: { parsed: { y: number } }) => `Win rate: ${ctx.parsed.y}%` },
          },
        },
        scales: {
          x: {
            ticks: { color: c.tick, font: { size: 10 } },
            grid: { color: c.grid },
          },
          y: {
            min: 0,
            max: 100,
            ticks: {
              color: c.tick,
              font: { size: 10 },
              callback: (v: string | number) => `${v}%`,
            },
            grid: { color: c.grid },
          },
        },
      },
    });
  }
</script>

<div class="mb-4 flex flex-wrap items-center justify-between gap-3">
  <h3 class="font-display text-lg font-semibold text-game-primary">Win rate trend</h3>
  <span
    class="border border-game bg-game-muted px-3 py-1 text-xs font-medium text-game-muted"
    style="border-radius: 9999px;"
    >{rangeLabel}</span
  >
</div>
{#if error}
  <p class="text-sm text-red-600">{error}</p>
{:else if data.length === 0}
  <p class="text-sm text-game-muted">No trend data yet.</p>
{:else}
  <div class="h-56">
    <canvas bind:this={canvas}></canvas>
  </div>
{/if}
