export interface LocalDependency {
  project: string
  path: string
  description?: string
  what: string
  note: string
  direction?: 'upstream' | 'downstream'
}

export interface GitDependency {
  project: string
  git: string
  ref: string
  description?: string
  what: string
  note: string
  direction?: 'upstream' | 'downstream'
}

export type Dependency = LocalDependency | GitDependency

export interface DepsConfig {
  upstream: Dependency[]
  downstream: Dependency[]
}

export interface FetchMeta {
  project: string
  git: string
  ref: string
  fetched_at: string
  files: string[]
}

export interface DependencyStatus {
  dep: Dependency
  direction: 'upstream' | 'downstream'
  type: 'local' | 'git'
  /** For local: whether the path exists and has .project-context/ */
  pathExists?: boolean
  hasContext?: boolean
  /** For git: whether the cache exists */
  cached?: boolean
  fetchedAt?: string
  cacheStale?: boolean
}

export function isGitDep(dep: Dependency): dep is GitDependency {
  return 'git' in dep
}

export function isLocalDep(dep: Dependency): dep is LocalDependency {
  return 'path' in dep
}
