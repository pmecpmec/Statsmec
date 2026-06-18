# Multi-stage build for the Astro static site.

# 1. Build stage: install deps and produce the static `dist/` output.
FROM node:20-alpine AS build
WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
# PUBLIC_* vars are baked in at build time; override via build args if needed.
ARG PUBLIC_API_URL
ARG PUBLIC_DEV_UI=false
ENV PUBLIC_API_URL=$PUBLIC_API_URL
ENV PUBLIC_DEV_UI=$PUBLIC_DEV_UI
RUN npm run build

# 2. Serve stage: lightweight static file server for the built output.
FROM node:20-alpine AS serve
WORKDIR /app
ENV NODE_ENV=production

COPY --from=build /app/dist ./dist

EXPOSE 5173
CMD ["npx", "--yes", "serve", "-s", "dist", "-l", "5173"]
