import chalk from 'chalk'
import Table from 'cli-table3'

export function errorMsg(msg: string): void {
  console.error(chalk.red('✖ ') + msg)
}

export function successMsg(msg: string): void {
  console.log(chalk.green('✔ ') + msg)
}

export function infoMsg(msg: string): void {
  console.log(chalk.cyan('ℹ ') + msg)
}

export function warnMsg(msg: string): void {
  console.log(chalk.yellow('⚠ ') + msg)
}

export function sectionHeader(title: string): void {
  console.log('\n' + chalk.bold(title))
  console.log(chalk.dim('─'.repeat(title.length)))
}

export function createTable(headers: string[]): InstanceType<typeof Table> {
  return new Table({
    head: headers.map((h) => chalk.bold.cyan(h)),
    style: { head: [], border: ['dim'] },
    chars: {
      top: '─', 'top-mid': '┬', 'top-left': '┌', 'top-right': '┐',
      bottom: '─', 'bottom-mid': '┴', 'bottom-left': '└', 'bottom-right': '┘',
      left: '│', 'left-mid': '├', mid: '─', 'mid-mid': '┼',
      right: '│', 'right-mid': '┤', middle: '│',
    },
  })
}

export function directionBadge(direction: 'upstream' | 'downstream'): string {
  return direction === 'upstream'
    ? chalk.blue('↑ upstream')
    : chalk.magenta('↓ downstream')
}

export function typeBadge(type: 'local' | 'git'): string {
  return type === 'local' ? chalk.dim('local') : chalk.dim('git')
}

export function statusBadge(ok: boolean, label?: string): string {
  if (ok) return chalk.green(label ?? 'ok')
  return chalk.red(label ?? 'missing')
}
