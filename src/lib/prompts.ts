import { select, input, confirm } from '@inquirer/prompts'

/**
 * Ask whether this project is upstream or downstream of the target.
 */
export async function promptDirection(
  currentProject: string,
  targetProject: string
): Promise<'upstream' | 'downstream'> {
  return select<'upstream' | 'downstream'>({
    message: `What is the relationship between ${currentProject} and ${targetProject}?`,
    choices: [
      {
        name: `${currentProject} consumes ${targetProject} (upstream)`,
        value: 'upstream',
        description: 'We import/use from them',
      },
      {
        name: `${targetProject} consumes ${currentProject} (downstream)`,
        value: 'downstream',
        description: 'They import/use from us',
      },
    ],
  })
}

/**
 * Ask what is shared between the two projects.
 */
export async function promptWhat(
  currentProject: string,
  targetProject: string,
  direction: 'upstream' | 'downstream'
): Promise<string> {
  const verb = direction === 'upstream' ? `consumes from ${targetProject}` : `exposes to ${targetProject}`
  const choices = [
    { name: 'Types / interfaces / schemas', value: 'Types, interfaces, schemas' },
    { name: 'API endpoints (REST, GraphQL, gRPC)', value: 'API endpoints' },
    { name: 'Shared utilities / helpers', value: 'Shared utilities and helpers' },
    { name: 'Database schemas / migrations', value: 'Database schemas and migrations' },
    { name: 'Custom...', value: '__custom__' },
  ]

  const choice = await select<string>({
    message: `What does ${currentProject} ${verb}?`,
    choices,
  })

  if (choice === '__custom__') {
    return input({ message: 'Describe what is shared:' })
  }
  return choice
}

/**
 * Ask for optional notes.
 */
export async function promptNote(): Promise<string> {
  const hasNote = await confirm({ message: 'Add any notes for this dependency?', default: false })
  if (!hasNote) return ''
  return input({ message: 'Notes:' })
}

/**
 * Ask which branch/ref to track for a git dependency.
 */
export async function promptRef(): Promise<string> {
  const choice = await select<string>({
    message: 'Which branch or ref to track?',
    choices: [
      { name: 'main (default)', value: 'main' },
      { name: 'master', value: 'master' },
      { name: 'Custom...', value: '__custom__' },
    ],
  })
  if (choice === '__custom__') {
    return input({ message: 'Branch, tag, or commit:' })
  }
  return choice
}

/**
 * Ask to confirm the inferred project name or enter a custom one.
 */
export async function promptProjectName(inferred: string): Promise<string> {
  const choice = await select<string>({
    message: `Project name? (inferred: ${inferred})`,
    choices: [
      { name: `${inferred} (use inferred)`, value: inferred },
      { name: 'Custom...', value: '__custom__' },
    ],
  })
  if (choice === '__custom__') {
    return input({ message: 'Project name:' })
  }
  return choice
}

/**
 * Ask which sibling project to add as a dependency.
 */
export async function promptSiblingProject(
  siblings: Array<{ name: string; path: string }>
): Promise<string> {
  const choices = siblings.map((s) => ({
    name: `${s.name} (${s.path})`,
    value: s.path,
  }))
  choices.push({ name: 'Enter path manually...', value: '__manual__' })

  const choice = await select<string>({
    message: 'Which project?',
    choices,
  })

  if (choice === '__manual__') {
    return input({ message: 'Path to project:' })
  }
  return choice
}

/**
 * Ask user to confirm a reciprocal dependency update in the target project.
 */
export async function promptReciprocal(targetProject: string): Promise<boolean> {
  return confirm({
    message: `Also update ${targetProject}'s dependencies.json with the reverse relationship?`,
    default: true,
  })
}
