import { defineCommand } from 'citty'
import { existsSync, readdirSync } from 'node:fs'
import { join, resolve, relative, basename } from 'node:path'
import chalk from 'chalk'
import { findContextDir, readProjectName } from '../lib/context.js'
import { readDeps, initDeps, addDep, writeDeps } from '../lib/deps.js'
import { fetchGitDep, isGitUrl, inferProjectName, extractDescription } from '../lib/git.js'
import {
  promptDirection,
  promptWhat,
  promptNote,
  promptRef,
  promptProjectName,
  promptSiblingProject,
  promptReciprocal,
} from '../lib/prompts.js'
import { errorMsg, infoMsg, successMsg, warnMsg, sectionHeader } from '../lib/display.js'
import { select } from '@inquirer/prompts'

export const addDepCommand = defineCommand({
  meta: {
    name: 'add-dep',
    description: 'Add a cross-project dependency (local path or git URL)',
  },
  args: {
    target: {
      type: 'positional',
      description: 'Path to sibling project or git URL',
      required: false,
    },
    dir: {
      type: 'string',
      description: 'Project root directory',
      default: '.',
    },
  },
  async run({ args }) {
    const contextDir = findContextDir(args.dir ?? '.')
    if (!contextDir) {
      errorMsg('No .project-context/ directory found.')
      infoMsg('Run /project-context:init first.')
      process.exit(1)
    }

    const projectRoot = resolve(join(contextDir, '..'))
    const currentProject = readProjectName(contextDir)

    let target: string | undefined = args.target ?? undefined

    // Determine intent when no argument given
    if (!target) {
      const intent = await select<'local' | 'git'>({
        message: 'What type of dependency do you want to add?',
        choices: [
          {
            name: 'Local path (sibling project in this monorepo)',
            value: 'local',
          },
          {
            name: 'Git URL (remote repository)',
            value: 'git',
          },
        ],
      })

      if (intent === 'local') {
        target = await pickSiblingPath(projectRoot)
      } else {
        const { input } = await import('@inquirer/prompts')
        target = await input({ message: 'Git repository URL:' })
      }
    }

    if (isGitUrl(target)) {
      await addGitDep(target, contextDir, currentProject)
    } else {
      await addLocalDep(target, contextDir, projectRoot, currentProject)
    }
  },
})

// ─── Local path flow ──────────────────────────────────────────────────────────

async function addLocalDep(
  targetPath: string,
  contextDir: string,
  projectRoot: string,
  currentProject: string
): Promise<void> {
  const absTarget = resolve(join(projectRoot, targetPath))

  if (!existsSync(absTarget)) {
    errorMsg(`Path '${targetPath}' does not exist.`)
    process.exit(1)
  }

  if (resolve(absTarget) === resolve(projectRoot)) {
    errorMsg('A project cannot depend on itself.')
    process.exit(1)
  }

  const targetContextDir = join(absTarget, '.project-context')
  const targetName = existsSync(targetContextDir)
    ? readProjectName(targetContextDir)
    : basename(absTarget)

  const relativePath = relative(projectRoot, absTarget)

  sectionHeader(`Adding local dependency: ${currentProject} → ${targetName}`)

  const direction = await promptDirection(currentProject, targetName)
  const what = await promptWhat(currentProject, targetName, direction)
  const note = await promptNote()

  // Compute description from target's brief.md
  let description: string | undefined
  if (existsSync(targetContextDir)) {
    description = extractDescription(join(targetContextDir, 'brief.md')) ?? undefined
  }

  const dep = {
    project: targetName,
    path: relativePath,
    ...(description ? { description } : {}),
    what,
    note,
  }

  let config = readDeps(contextDir) ?? initDeps(contextDir)

  try {
    config = addDep(config, direction, dep)
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err)
    errorMsg(msg)
    process.exit(1)
  }

  writeDeps(contextDir, config)
  successMsg(`Added ${chalk.bold(targetName)} as ${direction} dependency`)

  if (description) {
    infoMsg(`Description: ${description}`)
  }
  infoMsg(`What: ${what}`)

  // Reciprocal update
  if (existsSync(targetContextDir)) {
    const doReciprocal = await promptReciprocal(targetName)
    if (doReciprocal) {
      const reverseDirection = direction === 'upstream' ? 'downstream' : 'upstream'
      const reversePath = relative(absTarget, projectRoot)
      const reverseDep = {
        project: currentProject,
        path: reversePath,
        what,
        note,
      }

      let targetConfig = readDeps(targetContextDir) ?? initDeps(targetContextDir)
      try {
        targetConfig = addDep(targetConfig, reverseDirection, reverseDep)
        writeDeps(targetContextDir, targetConfig)
        successMsg(`Updated ${targetName}'s dependencies.json (reciprocal)`)
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : String(err)
        warnMsg(`Reciprocal update skipped: ${msg}`)
      }
    }
  }
}

// ─── Git URL flow ─────────────────────────────────────────────────────────────

async function addGitDep(
  gitUrl: string,
  contextDir: string,
  currentProject: string
): Promise<void> {
  const ref = await promptRef()
  const inferred = inferProjectName(gitUrl)
  const projectName = await promptProjectName(inferred)

  sectionHeader(`Adding git dependency: ${currentProject} → ${projectName}`)

  const direction = await promptDirection(currentProject, projectName)
  const what = await promptWhat(currentProject, projectName, direction)
  const note = await promptNote()

  const dep = {
    project: projectName,
    git: gitUrl,
    ref,
    what,
    note,
  }

  let config = readDeps(contextDir) ?? initDeps(contextDir)

  try {
    config = addDep(config, direction, dep)
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err)
    errorMsg(msg)
    process.exit(1)
  }

  writeDeps(contextDir, config)
  successMsg(`Added ${chalk.bold(projectName)} as ${direction} git dependency`)

  // Auto-fetch remote context
  infoMsg('Fetching remote .project-context/...')
  const result = await fetchGitDep(dep, contextDir)

  if (result.status === 'ok') {
    successMsg(`Fetched ${result.files?.length ?? 0} files from ${projectName}`)

    // Try to compute description from fetched brief.md
    const { projectCacheDir } = await import('../lib/cache.js')
    const briefPath = join(projectCacheDir(contextDir, projectName), 'brief.md')
    const description = extractDescription(briefPath)

    if (description) {
      // Update the dep entry with the computed description
      const updatedConfig = readDeps(contextDir)!
      const depList = updatedConfig[direction]
      const idx = depList.findIndex((d) => d.project === projectName)
      if (idx >= 0) {
        depList[idx] = { ...depList[idx], description }
        writeDeps(contextDir, updatedConfig)
        infoMsg(`Description: ${description}`)
      }
    }
  } else if (result.status === 'no_context') {
    warnMsg(`Remote has no .project-context/: ${result.message}`)
    infoMsg('Dependency added to dependencies.json. Run `pc fetch-deps` to retry later.')
  } else {
    warnMsg(`Fetch failed: ${result.error}`)
    infoMsg('Dependency added to dependencies.json. Run `pc fetch-deps` to retry later.')
  }
}

// ─── Sibling discovery ────────────────────────────────────────────────────────

async function pickSiblingPath(projectRoot: string): Promise<string> {
  // Discover sibling directories that have .project-context/
  const parentDir = resolve(join(projectRoot, '..'))
  const siblings: Array<{ name: string; path: string }> = []

  try {
    const entries = readdirSync(parentDir, { withFileTypes: true })
    for (const entry of entries) {
      if (!entry.isDirectory()) continue
      const absPath = join(parentDir, entry.name)
      if (resolve(absPath) === resolve(projectRoot)) continue
      if (existsSync(join(absPath, '.project-context'))) {
        siblings.push({
          name: readProjectName(join(absPath, '.project-context')),
          path: relative(projectRoot, absPath),
        })
      }
    }
  } catch {}

  if (siblings.length > 0) {
    return promptSiblingProject(siblings)
  }

  // No siblings found — ask for manual input
  const { input } = await import('@inquirer/prompts')
  return input({ message: 'Path to project (relative to current project):' })
}
