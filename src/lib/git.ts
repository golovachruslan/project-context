import { mkdirSync, existsSync, rmSync, readdirSync, readFileSync } from 'node:fs'
import { join } from 'node:path'
import { tmpdir } from 'node:os'
import { execa } from 'execa'
import { copyContextToCache, writeFetchMeta, getCacheDir } from './cache.js'
import type { GitDependency } from '../types.js'

export interface FetchResult {
  project: string
  status: 'ok' | 'error' | 'no_context'
  files?: string[]
  fetchedAt?: string
  cachedPath?: string
  error?: string
  message?: string
}

/**
 * Fetch the .project-context/ directory from a single git dependency
 * using sparse-checkout (no application code transferred).
 */
export async function fetchGitDep(
  dep: GitDependency,
  contextDir: string
): Promise<FetchResult> {
  const { project, git: gitUrl, ref = 'HEAD' } = dep
  const cacheDir = getCacheDir(contextDir)
  const projectCache = join(cacheDir, project)

  const tmpDir = join(tmpdir(), `pctx-${project}-${Date.now()}`)
  const repoDir = join(tmpDir, 'repo')

  try {
    mkdirSync(tmpDir, { recursive: true })

    // Sparse clone — only downloads tree objects, no blobs yet
    const cloneArgs = [
      'clone',
      '--depth', '1',
      '--filter=blob:none',
      '--sparse',
    ]
    if (ref !== 'HEAD') {
      cloneArgs.push('--branch', ref)
    }
    cloneArgs.push(gitUrl, repoDir)

    try {
      await execa('git', cloneArgs, { timeout: 120_000 })
    } catch (err: unknown) {
      const message = err instanceof Error ? (err as Error).message : String(err)
      return { project, status: 'error', error: `git clone failed: ${message}` }
    }

    // Restrict checkout to .project-context/ only — triggers blob download for that dir
    try {
      await execa('git', ['sparse-checkout', 'set', '.project-context'], {
        cwd: repoDir,
        timeout: 60_000,
      })
    } catch (err: unknown) {
      const message = err instanceof Error ? (err as Error).message : String(err)
      return { project, status: 'error', error: `git sparse-checkout failed: ${message}` }
    }

    const clonedContext = join(repoDir, '.project-context')
    if (!existsSync(clonedContext)) {
      return {
        project,
        status: 'no_context',
        message: 'Remote repository has no .project-context/ directory',
      }
    }

    // Count only files (skip subdirs like plans/)
    const fileEntries = readdirSync(clonedContext, { withFileTypes: true }).filter(
      (e) => e.isFile()
    )
    if (fileEntries.length === 0) {
      return {
        project,
        status: 'no_context',
        message: '.project-context/ exists but contains no files',
      }
    }

    // Copy context files to cache
    const copiedFiles = copyContextToCache(clonedContext, projectCache)
    const fetchedAt = new Date().toISOString()

    writeFetchMeta(projectCache, {
      project,
      git: gitUrl,
      ref,
      fetched_at: fetchedAt,
      files: copiedFiles,
    })

    return {
      project,
      status: 'ok',
      files: copiedFiles,
      fetchedAt,
      cachedPath: projectCache,
    }
  } finally {
    if (existsSync(tmpDir)) {
      rmSync(tmpDir, { recursive: true, force: true })
    }
  }
}

/**
 * Validate that a string looks like a git URL.
 */
export function isGitUrl(str: string): boolean {
  return (
    str.startsWith('https://') ||
    str.startsWith('git@') ||
    str.startsWith('ssh://') ||
    str.endsWith('.git')
  )
}

/**
 * Infer a project name from a git URL (last path segment without .git).
 */
export function inferProjectName(gitUrl: string): string {
  const last = gitUrl.split('/').at(-1) ?? gitUrl
  return last.replace(/\.git$/, '')
}

/**
 * Extract a brief description from a brief.md file in the cache.
 */
export function extractDescription(briefPath: string): string | null {
  if (!existsSync(briefPath)) return null
  try {
    const content = readFileSync(briefPath, 'utf-8')
    // Try to get the first non-heading, non-empty line in the Overview section
    const lines = content.split('\n')
    let inOverview = false
    for (const line of lines) {
      if (/^##\s+Overview/i.test(line)) {
        inOverview = true
        continue
      }
      if (inOverview && /^##/.test(line)) break
      if (inOverview && line.trim() && !line.startsWith('#')) {
        // Strip markdown bold/italic
        return line.trim().replace(/\*\*/g, '').replace(/\*/g, '').slice(0, 120)
      }
    }
  } catch {}
  return null
}
