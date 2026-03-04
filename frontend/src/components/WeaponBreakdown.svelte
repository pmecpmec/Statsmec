<script lang="ts">
  import { onMount } from 'svelte';

  let { apiUrl = 'http://127.0.0.1:8000/api/v1' } = $props();

  type WeaponAgg = { weapon: string; accuracy: number };
  let weapons: WeaponAgg[] = $state([]);
  let error = $state('');
  let canvas: HTMLCanvasElement | undefined = $state(undefined);

  const COLORS = ['#7c3aed', '#8b5cf6', '#a78bfa', '#c084fc', '#f59e0b', '#22c55e', '#3b82f6', '#ef4444'];

  onMount(async () => {
    try {
      const res = await fetch(`${apiUrl}/analytics/users/1`);
      const json = await res.json();
      const heatmaps = json.weapon_heatmaps ?? {};
      weapons = Object.entries(heatmaps)
        .map(([weapon, maps]: [string, any]) => {
          const cells = (maps as any[]).flatMap((m: any) => m.cells ?? []);
          const avg = cells.length ? cells.reduce((s: number, c: any) => s + c.intensity, 0) / cells.length : 0;
          return { weapon, accuracy: Math.round(avg * 100) };
        })
        .sort((a, b) => b.accuracy - a.accuracy)
        .slice(0, 8);
      if (weapons.length && canvas) drawChart();
    } catch {
      error = 'Could not load weapon data.';
    }
  });

  async function drawChart() {
    if (!canvas) return;
    const { Chart, registerables } = await import('chart.js');
    Chart.register(...registerables);

    new Chart(canvas, {
      type: 'bar',
      data: {
        labels: weapons.map((w) => w.weapon),
        datasets: [
          {
            label: 'Accuracy %',
            data: weapons.map((w) => w.accuracy),
            backgroundColor: weapons.map((_, i) => COLORS[i % COLORS.length]),
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
            backgroundColor: '#1a1a2e',
            borderColor: 'rgba(255,255,255,0.1)',
            borderWidth: 1,
            titleColor: '#fff',
            bodyColor: '#a1a1aa',
            callbacks: { label: (ctx: any) => `${ctx.parsed.x}%` },
          },
        },
        scales: {
          x: {
            ticks: { color: '#71717a', font: { size: 10 }, callback: (v: any) => `${v}%` },
            grid: { color: 'rgba(255,255,255,0.05)' },
          },
          y: {
            ticks: { color: '#e4e4e7', font: { size: 12 } },
            grid: { display: false },
          },
        },
      },
    });
  }
</script>

<h3 class="text-lg font-bold text-white mb-4">Weapon Accuracy</h3>
{#if error}
  <p class="text-red-400 text-sm">{error}</p>
{:else if weapons.length === 0}
  <p class="text-zinc-500 text-sm">No weapon data yet.</p>
{:else}
  <div class="h-56">
    <canvas bind:this={canvas}></canvas>
  </div>
{/if}
