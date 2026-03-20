import { defineCommand } from 'citty'
import chalk from 'chalk'
import { findContextDir } from '../lib/context.js'
import { readDeps } from '../lib/deps.js'
import { fetchGitDep } from '../lib/git.js'
import { errorMsg, infoMsg, successMsg, warnMsg, sectionHeader } from '../lib/display.js'
import { isGitDep } from '../types.js'

export const fetchDepsCommand = defineCommand({
  meta: {
    name: 'fetch-deps',
    description: 'Fetch/refresh .project-context/ from git dependencies',
  },
  args: {
    project: {
      type: 'positional',
      description: 'Fetch only this project (by name)',
      required: false,
    },
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
      infoMsg('Run /project-context:init first.')
      process.exit(1)
    }

    const config = readDeps(contextDir)
    if (!config) {
      infoMsg('No dependencies.json found. Run `pc add-dep` to add a dependency.')
      return
    }

    // Collect all git deps
    const allEntries = [
      ...config.upstream.map((dep) => ({ dep, direction: 'upstream' as const })),
      ...config.downstream.map((dep) => ({ dep, direction: 'downstream' as const })),
    ]

    let gitDeps = allEntries.filter(({ dep }) => isGitDep(dep))

    if (gitDeps.length === 0) {
      infoMsg('No git dependencies found in dependencies.json.')
      infoMsg('Add one with: pc add-dep <git-url>')
      return
    }

    // Filter by project name if specified
    const projectFilter = args.project
    if (projectFilter) {
      gitDeps = gitDeps.filter(({ dep }) => dep.project === projectFilter)
      if (gitDeps.length === 0) {
        errorMsg(`No git dependency named '${projectFilter}' found.`)
        process.exit(1)
      }
    }

    if (!args.json) {
      sectionHeader(`Fetching ${gitDeps.length} git dep${gitDeps.length > 1 ? 's' : ''}`)
    }

    const results = []

    for (const { dep } of gitDeps) {
      if (!isGitDep(dep)) continue

      if (!args.json) {
        process.stdout.write(chalk.dim(`  Fetching ${dep.project}...`))
      }

      const result = await fetchGitDep(dep, contextDir)
      results.push(result)

      if (!args.json) {
        // Clear the "Fetching..." line
        process.stdout.write('\r' + ' '.repeat(50) + '\r')

        if (result.status === 'ok') {
          successMsg(
            `${chalk.bold(dep.project)} — ${result.files?.length ?? 0} files` +
              chalk.dim(` (ref: ${dep.ref})`)
          )
        } else if (result.status === 'no_context') {
          warnMsg(`${chalk.bold(dep.project)} — ${result.message}`)
        } else {
          errorMsg(`${chalk.bold(dep.project)} — ${result.error}`)
        }
      }
    }

    if (args.json) {
      const okCount = results.filter((r) => r.status === 'ok').length
      const errCount = results.filter((r) => r.status === 'error').length
      const noCtx = results.filter((r) => r.status === 'no_context').length
      console.log(
        JSON.stringify(
          { fetched: okCount, errors: errCount, no_context: noCtx, total: results.length, results },
          null,
          2
        )
      )
      return
    }

    // Summary
    const ok = results.filter((r) => r.status === 'ok').length
    const err = results.filter((r) => r.status === 'error').length
    console.log()
    if (err > 0) {
      warnMsg(`${ok} fetched, ${err} failed`)
    } else {
      successMsg(`${ok} dep${ok > 1 ? 's' : ''} fetched successfully`)
    }
  },
})
