import { defineCommand, runMain } from 'citty'
import { listDepsCommand } from './commands/list-deps.js'
import { addDepCommand } from './commands/add-dep.js'
import { fetchDepsCommand } from './commands/fetch-deps.js'

const main = defineCommand({
  meta: {
    name: 'pc',
    version: '0.1.0',
    description: 'Manage project-context cross-project dependencies',
  },
  subCommands: {
    'list-deps': listDepsCommand,
    'add-dep': addDepCommand,
    'fetch-deps': fetchDepsCommand,
  },
})

runMain(main)
