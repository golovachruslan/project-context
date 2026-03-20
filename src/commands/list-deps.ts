import { defineCommand } from 'citty'
import { existsSync, readFileSync } from 'node:fs'
import { join } from 'node:path'
import { findContextDir } from '../lib/context.js'
import { readDeps, allDeps } from '../lib/deps.js'
import {
  createTable,
  directionBadge,
  typeBadge,
  statusBadge,
  errorMsg,
  infoMsg,
  sectionHeader,
} from '../lib/display.js'
import { isGitDep, isLocalDep, type DependencyStatus } from '../types.js'
import chalk from 'chalk'

export const listDepsCommand = defineCommand({
  meta: {
    name: 'list-deps',
    description: 'List all cross-project dependencies with status',
  },
  args: {
    dir: {
      type: 'string',
      description: 'Project root directory',
      default: '.',
    },
    json: {
      type: 'boolean',
      description: 'Output as JSON',
      default: false,
    },
  },
  async run({ args }) {
    const contextDir = findContextDir(args.dir ?? '.')
    if (!contextDir) {
      errorMsg('No .project-context/ directory found.')
      infoMsg('Run /project-context:init first to initialize project context.')
      process.exit(1)
    }

    const config = readDeps(contextDir)
    if (!config) {
      infoMsg('No dependencies.json found.')
      infoMsg('Run `pc add-dep` to add your first dependency.')
      return
    }

    const entries = allDeps(config)
    if (entries.length === 0) {
      infoMsg('No dependencies declared in dependencies.json.')
      infoMsg('Run `pc add-dep` to add your first dependency.')
      return
    }

    // Resolve status for each dep
    const statuses: DependencyStatus[] = entries.map(({ dep, direction }) => {
      if (isGitDep(dep)) {
        const cachePath = join(contextDir, '.deps-cache', dep.project)
        const cached = existsSync(cachePath)
        let fetchedAt: string | undefined
        let cacheStale = false

        if (cached) {
          const metaPath = join(cachePath, '.fetch-meta.json')
          if (existsSync(metaPath)) {
            try {
              const meta = JSON.parse(readFileSync(metaPath, 'utf-8'))
              fetchedAt = meta.fetched_at
              if (fetchedAt) {
                const age = Date.now() - new Date(fetchedAt).getTime()
                cacheStale = age > 7 * 24 * 60 * 60 * 1000 // 7 days
              }
            } catch {}
          }
        }

        return { dep, direction, type: 'git', cached, fetchedAt, cacheStale }
      } else if (isLocalDep(dep)) {
        const depPath = join(contextDir, '..', dep.path)
        const pathExists = existsSync(depPath)
        const hasContext = pathExists && existsSync(join(depPath, '.project-context'))
        return { dep, direction, type: 'local', pathExists, hasContext }
      }
      return { dep, direction, type: 'local' }
    })

    if (args.json) {
      console.log(JSON.stringify(statuses, null, 2))
      return
    }

    // Human-readable table
    sectionHeader(`Dependencies (${entries.length})`)

    const table = createTable(['Project', 'Direction', 'Type', 'Location', 'Status'])

    for (const s of statuses) {
      const { dep } = s
      const project = chalk.bold(dep.project)
      const direction = directionBadge(s.direction)
      const type = typeBadge(s.type)

      let location = ''
      let status = ''

      if (s.type === 'git' && isGitDep(dep)) {
        location = chalk.dim(`${dep.git.replace(/^https?:\/\//, '')} @${dep.ref}`)
        if (s.cached && s.cacheStale) {
          status = chalk.yellow('cached (stale)')
        } else if (s.cached) {
          status = chalk.green('cached')
          if (s.fetchedAt) {
            const d = new Date(s.fetchedAt)
            status += chalk.dim(` (${d.toLocaleDateString()})`)
          }
        } else {
          status = chalk.red('not fetched')
        }
      } else if (s.type === 'local' && isLocalDep(dep)) {
        location = chalk.dim(dep.path)
        if (!s.pathExists) {
          status = statusBadge(false, 'path missing')
        } else if (!s.hasContext) {
          status = chalk.yellow('no context')
        } else {
          status = statusBadge(true, 'ok')
        }
      }

      const desc = dep.description ? chalk.dim(`\n${dep.description}`) : ''
      table.push([project + desc, direction, type, location, status])
    }

    console.log(table.toString())

    // Summary hints
    const notFetched = statuses.filter((s) => s.type === 'git' && !s.cached)
    const stale = statuses.filter((s) => s.type === 'git' && s.cached && s.cacheStale)

    if (notFetched.length > 0) {
      infoMsg(`${notFetched.length} git dep(s) not fetched — run \`pc fetch-deps\``)
    }
    if (stale.length > 0) {
      infoMsg(`${stale.length} git dep(s) have stale cache — run \`pc fetch-deps\` to refresh`)
    }
  },
})
