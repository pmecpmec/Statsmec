import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1",
  timeout: 10000
});

type CacheEntry<T> = {
  value: T;
  timestamp: number;
};

const memoryCache = new Map<string, CacheEntry<unknown>>();
const DEFAULT_TTL_MS = 60_000;

export async function cachedGet<T>(
  url: string,
  ttlMs: number = DEFAULT_TTL_MS
): Promise<T> {
  const key = url;
  const existing = memoryCache.get(key) as CacheEntry<T> | undefined;
  const now = Date.now();

  if (existing && now - existing.timestamp < ttlMs) {
    return existing.value;
  }

  const response = await api.get<T>(url);
  memoryCache.set(key, { value: response.data, timestamp: now });
  return response.data;
}

export { api };

