import { defineBuildConfig } from 'unbuild'

export default defineBuildConfig({
  entries: ['src/index'],
  declaration: true,
  clean: true,
  rollup: {
    emitCJS: true,
    inlineDependencies: false,
  },
  externals: [
    'citty',
    '@inquirer/prompts',
    'chalk',
    'cli-table3',
    'execa',
  ],
})
