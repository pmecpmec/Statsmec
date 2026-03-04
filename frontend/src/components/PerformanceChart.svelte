<script lang="ts">
  import { onMount } from 'svelte';

  let { apiUrl = 'http://127.0.0.1:8000/api/v1' } = $props();

  type TrendPoint = { date: string; win_rate: number; matches: number };
  let data: TrendPoint[] = $state([]);
  let error = $state('');
  let canvas: HTMLCanvasElement | undefined = $state(undefined);

  onMount(async () => {
    try {
      const res = await fetch(`${apiUrl}/analytics/users/1`);
      const json = await res.json();
      data = json.win_rate_trend ?? [];
      if (data.length && canvas) drawChart();
    } catch {
      error = 'Could not load trends.';
    }
  });

  async function drawChart() {
    if (!canvas) return;
    const { Chart, registerables } = await import('chart.js');
    Chart.register(...registerables);

    new Chart(canvas, {
      type: 'line',
      data: {
        labels: data.map((d) => d.date),
        datasets: [
          {
            label: 'Win Rate',
            data: data.map((d) => Math.round(d.win_rate * 100)),
            borderColor: '#7c3aed',
            backgroundColor: 'rgba(124,58,237,0.1)',
            fill: true,
            tension: 0.4,
            pointRadius: 3,
            pointBackgroundColor: '#7c3aed',
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
            backgroundColor: '#1a1a2e',
            borderColor: 'rgba(255,255,255,0.1)',
            borderWidth: 1,
            titleColor: '#fff',
            bodyColor: '#a1a1aa',
            callbacks: { label: (ctx: any) => `Win Rate: ${ctx.parsed.y}%` },
          },
        },
        scales: {
          x: {
            ticks: { color: '#71717a', font: { size: 10 } },
            grid: { color: 'rgba(255,255,255,0.05)' },
          },
          y: {
            min: 0,
            max: 100,
            ticks: {
              color: '#71717a',
              font: { size: 10 },
              callback: (v: any) => `${v}%`,
            },
            grid: { color: 'rgba(255,255,255,0.05)' },
          },
        },
      },
    });
  }
</script>

<h3 class="text-lg font-bold text-white mb-4">Win Rate Trend</h3>
{#if error}
  <p class="text-red-400 text-sm">{error}</p>
{:else if data.length === 0}
  <p class="text-zinc-500 text-sm">No trend data yet.</p>
{:else}
  <div class="h-56">
    <canvas bind:this={canvas}></canvas>
  </div>
{/if}
