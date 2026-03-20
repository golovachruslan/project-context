import { existsSync, readFileSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'
import type { DepsConfig, Dependency } from '../types.js'

const EMPTY_CONFIG: DepsConfig = { upstream: [], downstream: [] }

/**
 * Read and parse dependencies.json from a .project-context directory.
 * Returns null if the file doesn't exist or is invalid.
 */
export function readDeps(contextDir: string): DepsConfig | null {
  const depsPath = join(contextDir, 'dependencies.json')
  if (!existsSync(depsPath)) return null
  try {
    const raw = readFileSync(depsPath, 'utf-8')
    const data = JSON.parse(raw) as Partial<DepsConfig>
    return {
      upstream: data.upstream ?? [],
      downstream: data.downstream ?? [],
    }
  } catch {
    return null
  }
}

/**
 * Write dependencies.json. Always writes the full file.
 */
export function writeDeps(contextDir: string, config: DepsConfig): void {
  const depsPath = join(contextDir, 'dependencies.json')
  writeFileSync(depsPath, JSON.stringify(config, null, 2) + '\n', 'utf-8')
}

/**
 * Initialize an empty dependencies.json if it doesn't exist.
 */
export function initDeps(contextDir: string): DepsConfig {
  const existing = readDeps(contextDir)
  if (existing) return existing
  writeDeps(contextDir, EMPTY_CONFIG)
  return { ...EMPTY_CONFIG }
}

/**
 * Add a dependency to the config. Throws if a duplicate is found.
 */
export function addDep(
  config: DepsConfig,
  direction: 'upstream' | 'downstream',
  dep: Dependency
): DepsConfig {
  const list = config[direction]
  const duplicate = list.find(
    (d) =>
      d.project === dep.project ||
      ('git' in dep && 'git' in d && d.git === dep.git)
  )
  if (duplicate) {
    throw new Error(`Dependency '${dep.project}' already exists as ${direction}`)
  }
  return {
    ...config,
    [direction]: [...list, dep],
  }
}

/**
 * Find a dependency by project name across upstream and downstream.
 */
export function findDep(
  config: DepsConfig,
  projectName: string
): { dep: Dependency; direction: 'upstream' | 'downstream' } | null {
  for (const direction of ['upstream', 'downstream'] as const) {
    const found = config[direction].find((d) => d.project === projectName)
    if (found) return { dep: found, direction }
  }
  return null
}

/**
 * All dependencies flattened with their direction.
 */
export function allDeps(
  config: DepsConfig
): Array<{ dep: Dependency; direction: 'upstream' | 'downstream' }> {
  return [
    ...config.upstream.map((dep) => ({ dep, direction: 'upstream' as const })),
    ...config.downstream.map((dep) => ({ dep, direction: 'downstream' as const })),
  ]
}
