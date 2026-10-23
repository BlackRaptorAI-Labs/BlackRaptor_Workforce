# Language reference — TypeScript

Load this only when the diff contains TypeScript (`*.ts`, `*.tsx`, `tsconfig.json`). Use it as a review lens: each item says what fails and how to check it.

## Checks (run by whoever holds Bash; a read-only reviewer cites the completion audit's run)

| Tool | Command | What it catches |
|---|---|---|
| compiler | `tsc --noEmit` | type errors across the project |
| linter | `eslint .` (with the project's config) | floating promises, unsafe `any`, risky patterns |
| tests | the project's test command | behaviour |
| dependencies | `npm audit` (or the `pnpm`/`yarn` equivalent) | dependencies with published vulnerabilities |

Quote each command's output in the evidence. A tool the project does not have installed is a gap to state, not a pass.

Test helpers that create a Git repository, and asserting on full output lines: `test-isolation.md` (shared by every language).

## Blocking
- External data (request bodies, query strings, messages, `JSON.parse` results, third-party responses) used through an `as` cast or `any` without runtime validation.
- A promise that is neither awaited nor handled (`void` or `.catch`) on a path that writes, deletes, pays, or authorizes: errors vanish and work runs out of order.
- `@ts-ignore`, `@ts-expect-error`, or the non-null `!` used to silence an error the code does not rule out.
- Object keys from input merged into an object (spread, `Object.assign`, deep merge) without excluding `__proto__`, `constructor`, and `prototype`.

## Should fix
- `==` where `===` is meant; truthiness checks that treat `0` or `""` as missing.
- `strict` (or `strictNullChecks`) off in the changed package's `tsconfig.json`.
- `try`/`catch` around a promise that is not awaited inside the `try`.

## Nit
- Exported functions without explicit return types; enums where a union of string literals would do.
