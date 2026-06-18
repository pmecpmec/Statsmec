<script lang="ts">
  let { current = 'cs2' }: { current?: 'cs2' | 'valorant' } = $props();
</script>

<div class="flex flex-col items-center gap-3 py-2">
  <span class="text-xs font-medium uppercase tracking-wider text-game-muted">Game switcher</span>
  <div
    class="inline-flex rounded-full border border-game bg-game-card p-1 shadow-sm"
    role="group"
    aria-label="Select game"
  >
    <a
      href="/"
      class="rounded-full px-5 py-2 text-sm font-semibold transition-all"
      class:bg-[var(--accent)]={current === 'cs2'}
      class:text-[#0b0f14]={current === 'cs2'}
      class:shadow-md={current === 'cs2'}
      class:text-game-muted={current !== 'cs2'}
      class:hover:text-game-primary={current !== 'cs2'}
    >
      CS2
    </a>
    <a
      href="/valorant"
      class="rounded-full px-5 py-2 text-sm font-semibold transition-all"
      class:bg-[var(--accent)]={current === 'valorant'}
      class:text-white={current === 'valorant'}
      class:shadow-md={current === 'valorant'}
      class:shadow-[0_0_20px_var(--glow-accent)]={current === 'valorant'}
      class:text-game-muted={current !== 'valorant'}
      class:hover:text-game-primary={current !== 'valorant'}
    >
      Valorant
    </a>
  </div>
</div>
