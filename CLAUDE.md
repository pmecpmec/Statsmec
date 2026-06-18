# Statsmec — Project Instructions

CS2 performance-analytics dashboard. Real-time stat-tracking en match-history voor Counter-Strike 2 spelers.

## Stack
- **Frontend:** Astro + Svelte, TypeScript, Tailwind CSS (`lucide-svelte` voor icons)
- **Backend:** Python 3.11, FastAPI, SQLAlchemy 2.0 (async), Poetry
- **Data:** PostgreSQL (asyncpg), Redis, MongoDB (motor)
- **Externe integraties:** FACEIT API, Riot/Valorant, Allstar highlights

## Owner
Pedro Eduardo Cardoso — [pmec.dev](https://pmec.dev/) · AD Software Developer @ Windesheim.

---

## 📚 Externe kennisbank (pmecbrain2)

Mijn persoonlijke kennisbank staat los van deze repo op:

```
C:\Users\pmec\Documents\pmecbrain2
```

Het zijn losse Markdown-notities (Obsidian-vault). **Lees relevante notities daar wanneer je
context nodig hebt over een techniek** in plaats van vanaf nul te redeneren. Belangrijke mappen
voor dit project:

### Frontend
`30-RESOURCES/frontend-web/` — o.a.:
- `React.md`, `React 19.md`, `React Components.md`, `React Performance.md`
- `Tailwind CSS.md`, `CSS.md`, `Framer Motion.md`, `Vite.md`
- `Frontend Performance.md`, `Core Web Vitals.md`
- `Accessibility Fundamentals.md`, `ARIA Patterns.md`

### Backend & database
`30-RESOURCES/backend-db/` — o.a.:
- `Node.js.md`, `PostgreSQL.md`, `Prisma.md`, `Supabase.md`
- `REST API Design.md`, `GraphQL API Design.md`, `WebSocket APIs.md`
- `Authentication Patterns.md`, `API Security.md`, `Caching Strategies.md`
- `Database Design Patterns.md`, `Data Modeling.md`, `Query Optimization.md`

### Taal & snippets
`30-RESOURCES/talen/` — o.a.:
- `TypeScript.md`, `TypeScript Strict Mode.md`, `JavaScript.md`
- `React-Hooks-Snippets.md`, `Database-Snippets.md`, `Code-Snippets-Library.md`

### DevOps & architectuur
`30-RESOURCES/devops-cloud/` — o.a.:
- `Docker Basics.md`, `Docker Advanced.md`, `Vercel Deployment.md`
- `CI-CD Patterns.md`, `Git Workflow.md`
- `Clean Architecture.md`, `Design Patterns.md`, `Logging Patterns.md`

### Data (voor stat-verwerking)
`30-RESOURCES/ai-ml/` — `Data Cleaning.md`, `Feature Engineering.md`

> Deze notities zijn **referentie/voorkeuren**, geen strikte regels. Volg ze waar ze passen
> bij deze codebase; wijk gemotiveerd af waar de repo iets anders vraagt.

---

## Werkafspraken
- TypeScript strict; geen `any` zonder reden.
- Components klein en herbruikbaar houden.
- Schrijf/Update tests bij niet-triviale logica.
- Commit-berichten kort en in imperatief.
- Vraag bij twijfel over architectuur eerst, voordat je groot refactort.
