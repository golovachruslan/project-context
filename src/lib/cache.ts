import { existsSync, mkdirSync, writeFileSync, readFileSync, rmSync, readdirSync, cpSync } from 'node:fs'
import { join } from 'node:path'
import type { FetchMeta } from '../types.js'

const CACHE_DIR_NAME = '.deps-cache'
const META_FILENAME = '.fetch-meta.json'
const GITIGNORE_CONTENT = '# Auto-generated — cached git dependency contexts\n*\n!.gitignore\n'

/**
 * Get (and ensure) the .deps-cache directory inside the given context dir.
 */
export function getCacheDir(contextDir: string): string {
  const cacheDir = join(contextDir, CACHE_DIR_NAME)
  mkdirSync(cacheDir, { recursive: true })

  const gitignore = join(cacheDir, '.gitignore')
  if (!existsSync(gitignore)) {
    writeFileSync(gitignore, GITIGNORE_CONTENT, 'utf-8')
  }

  return cacheDir
}

/**
 * Path to a specific project's cache dir.
 */
export function projectCacheDir(contextDir: string, project: string): string {
  return join(contextDir, CACHE_DIR_NAME, project)
}

/**
 * Read fetch metadata for a cached project.
 */
export function readFetchMeta(contextDir: string, project: string): FetchMeta | null {
  const metaPath = join(projectCacheDir(contextDir, project), META_FILENAME)
  if (!existsSync(metaPath)) return null
  try {
    return JSON.parse(readFileSync(metaPath, 'utf-8')) as FetchMeta
  } catch {
    return null
  }
}

/**
 * Write fetch metadata for a cached project.
 */
export function writeFetchMeta(cacheDir: string, meta: FetchMeta): void {
  writeFileSync(join(cacheDir, META_FILENAME), JSON.stringify(meta, null, 2) + '\n', 'utf-8')
}

/**
 * Copy context files from a temp directory to the project cache dir.
 * Clears any existing cache first.
 */
export function copyContextToCache(
  sourceDir: string,
  cacheDir: string
): string[] {
  // Clear old cache (keep the dir itself)
  if (existsSync(cacheDir)) {
    rmSync(cacheDir, { recursive: true })
  }
  mkdirSync(cacheDir, { recursive: true })

  // Copy only files (skip subdirectories like plans/)
  const entries = readdirSync(sourceDir, { withFileTypes: true })
  const copiedFiles: string[] = []
  for (const entry of entries) {
    if (entry.isFile()) {
      cpSync(join(sourceDir, entry.name), join(cacheDir, entry.name))
      copiedFiles.push(entry.name as string)
    }
  }
  return copiedFiles
}

/**
 * List context files in a project cache (excluding .fetch-meta.json).
 */
export function listCachedFiles(contextDir: string, project: string): string[] {
  const dir = projectCacheDir(contextDir, project)
  if (!existsSync(dir)) return []
  return readdirSync(dir).filter((f) => f !== META_FILENAME && !f.startsWith('.'))
}

/**
 * Remove a project's cache directory.
 */
export function removeProjectCache(contextDir: string, project: string): boolean {
  const dir = projectCacheDir(contextDir, project)
  if (!existsSync(dir)) return false
  rmSync(dir, { recursive: true })
  return true
}

/**
 * Check if a project cache is stale (>7 days old).
 */
export function isCacheStale(contextDir: string, project: string): boolean {
  const meta = readFetchMeta(contextDir, project)
  if (!meta?.fetched_at) return false
  const age = Date.now() - new Date(meta.fetched_at).getTime()
  return age > 7 * 24 * 60 * 60 * 1000
}
