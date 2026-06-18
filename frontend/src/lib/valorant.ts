/**
 * Static Valorant agent metadata + queue labels.
 *
 * This is canonical, public game knowledge (an agent's role, a queue's display
 * name) — NOT player performance data. It only classifies/labels values that
 * already come from the Riot API (agent names, queue ids), so the UI can apply
 * role identity colors without fabricating any stats.
 */

export type AgentRole = 'Duelist' | 'Initiator' | 'Controller' | 'Sentinel';

const AGENT_ROLES: Record<string, AgentRole> = {
  // Duelists
  jett: 'Duelist',
  phoenix: 'Duelist',
  raze: 'Duelist',
  reyna: 'Duelist',
  yoru: 'Duelist',
  neon: 'Duelist',
  iso: 'Duelist',
  waylay: 'Duelist',
  // Initiators
  sova: 'Initiator',
  breach: 'Initiator',
  skye: 'Initiator',
  'kay/o': 'Initiator',
  kayo: 'Initiator',
  fade: 'Initiator',
  gekko: 'Initiator',
  tejo: 'Initiator',
  // Controllers
  brimstone: 'Controller',
  omen: 'Controller',
  viper: 'Controller',
  astra: 'Controller',
  harbor: 'Controller',
  clove: 'Controller',
  // Sentinels
  sage: 'Sentinel',
  cypher: 'Sentinel',
  killjoy: 'Sentinel',
  chamber: 'Sentinel',
  deadlock: 'Sentinel',
  vyse: 'Sentinel',
};

const ROLE_VARS: Record<AgentRole, string> = {
  Duelist: 'var(--role-duelist)',
  Initiator: 'var(--role-initiator)',
  Controller: 'var(--role-controller)',
  Sentinel: 'var(--role-sentinel)',
};

/** Resolve an agent's role from its (Riot-provided) name, or null if unknown. */
export function agentRole(name: string | null | undefined): AgentRole | null {
  if (!name) return null;
  return AGENT_ROLES[name.trim().toLowerCase()] ?? null;
}

/** CSS color var for a role; falls back to a neutral token for unknown agents. */
export function roleColor(role: AgentRole | null): string {
  return role ? ROLE_VARS[role] : 'var(--role-default)';
}

const QUEUE_LABELS: Record<string, string> = {
  competitive: 'Competitive',
  unrated: 'Unrated',
  swiftplay: 'Swiftplay',
  spikerush: 'Spike Rush',
  deathmatch: 'Deathmatch',
  ggteam: 'Escalation',
  onefa: 'Replication',
  hurm: 'Team Deathmatch',
  premier: 'Premier',
  newmap: 'New Map',
  '': 'Custom',
};

/** Human label for a Riot queue id (e.g. "competitive" -> "Competitive"). */
export function queueLabel(queue: string | null | undefined): string | null {
  if (queue === null || queue === undefined) return null;
  const key = queue.trim().toLowerCase();
  if (key in QUEUE_LABELS) return QUEUE_LABELS[key];
  // Unknown id: title-case the raw value rather than inventing a name.
  return key
    ? key.charAt(0).toUpperCase() + key.slice(1)
    : 'Custom';
}
