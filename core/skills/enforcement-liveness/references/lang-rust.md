# Language reference — Rust

Load this only when the diff contains Rust (`*.rs`, `Cargo.toml`). Use it as a review lens: each item says what fails and how to check it.

## Run these first

| Tool | Command | What it catches |
|---|---|---|
| clippy | `cargo clippy --all-targets -- -D warnings` | common bugs and unidiomatic code, as errors |
| tests | `cargo test` | behaviour; add `--all-features` if the crate uses features |
| format | `cargo fmt --check` | formatting drift |
| advisories | `cargo audit` | dependencies with published security advisories |

Quote each command's output in the evidence. A tool the project does not have installed is a gap to state, not a pass.

## Blocking
- `unwrap()`, `expect()` or indexing that can panic on a request, message, or file the program did not create.
- An `unsafe` block with no comment stating the invariant that makes it sound, or one whose invariant the surrounding code does not uphold.
- A lock guard (`Mutex`, `RwLock`) held across an `.await`, or blocking I/O inside an async task.
- Arithmetic on sizes, money, or counters that can overflow: release builds wrap silently. Use `checked_`, `saturating_` or a wider type.
- A panic that can cross an FFI boundary.

## Should fix
- Errors converted to strings early, losing the source; a library returning `Box<dyn Error>` where callers need to match.
- `clone()` in a hot loop to satisfy the borrow checker where a borrow would do.
- `#[allow(...)]` added to silence a clippy lint without a reason in a comment.

## Nit
- Public items without doc comments; `use` lists that glob-import a whole module.
