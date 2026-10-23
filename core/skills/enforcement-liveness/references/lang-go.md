# Language reference — Go

Load this only when the diff contains Go (`*.go`, `go.mod`). Use it as a review lens, not a style guide: each item says what fails and how to check it.

## Checks (run by whoever holds Bash; a read-only reviewer cites the completion audit's run)

| Tool | Command | What it catches |
|---|---|---|
| vet | `go vet ./...` | suspicious constructs: printf mismatches, copied locks, unreachable code |
| staticcheck | `staticcheck ./...` | bugs and dead code vet misses |
| race detector | `go test -race ./...` | data races the tests exercise |
| vulnerabilities | `govulncheck ./...` | known-vulnerable dependencies the code actually calls |

Quote each command's output in the evidence. A tool the project does not have installed is a gap to state, not a pass.

Test helpers that create a Git repository, and asserting on full output lines: `test-isolation.md` (shared by every language).

## Blocking
- An error return ignored or assigned to `_` on a path that writes, deletes, pays, or authorizes.
- A goroutine with no way to stop (no context cancellation, no closed channel): it leaks per request.
- Shared state (maps, slices, counters) written from more than one goroutine without a lock or channel.
- A `context.Context` dropped or replaced with `context.Background()` inside a request path, so timeouts and cancellation stop working.
- An HTTP response body that is not closed, or a client with no timeout.

## Should fix
- Errors wrapped without `%w`, so callers cannot use `errors.Is` or `errors.As`.
- `defer` inside a loop that holds a file, lock, or connection until the function returns.
- A loop variable captured by a goroutine or closure (check the module's Go version: the per-iteration semantics changed in Go 1.22).
- A write to a nil map, or a `panic` used for ordinary error handling.

## Nit
- Exported names without doc comments; package names that repeat in identifiers.
