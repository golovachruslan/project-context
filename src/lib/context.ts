import { existsSync, readFileSync } from 'node:fs'
import { join, resolve } from 'node:path'

/**
 * Find the .project-context directory starting from the given dir.
 * Returns the absolute path, or null if not found.
 */
export function findContextDir(startDir = '.'): string | null {
  const contextDir = resolve(join(startDir, '.project-context'))
  if (existsSync(contextDir)) {
    return contextDir
  }
  return null
}

/**
 * Returns the project root (parent of .project-context).
 */
export function findProjectRoot(startDir = '.'): string | null {
  const contextDir = findContextDir(startDir)
  if (!contextDir) return null
  return resolve(join(contextDir, '..'))
}

/**
 * Read the project name from brief.md, falling back to directory name.
 */
export function readProjectName(contextDir: string): string {
  const briefPath = join(contextDir, 'brief.md')
  if (existsSync(briefPath)) {
    const content = readFileSync(briefPath, 'utf-8')
    const match = content.match(/\*\*Project Name:\*\*\s*(.+)/)
    if (match) return match[1].trim()
  }
  // Fall back to parent directory name
  return resolve(join(contextDir, '..')).split('/').at(-1) ?? 'unknown'
}
