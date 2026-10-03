# Common false positives (generic)

Patterns that often read as a defect and usually are not. Before writing a finding that matches one
of these, check the reason it is usually safe. If that reason does not hold in this code, the
finding stands; say why in `evidence`. Per-domain lists belong to each gate's owner and extend this
one.

1. **Input validated upstream.** A handler that does not re-validate input that a schema, middleware
   or gateway already validated on every path into it. Check every path, not one.
2. **Test-only code.** Hard-coded secrets, disabled checks or weak randomness inside test fixtures or
   test helpers that never ship.
3. **Framework default already safe.** Missing escaping, CSRF or parameterisation where the framework
   applies it by default. Cite the framework documentation, or the claim is ASSUMED.
4. **Unreachable branch.** A defect in code no caller reaches. Show the caller search before calling
   it live.
5. **Intentional, documented behaviour.** A design decision recorded in the spec or an ADR, such as
   eventual consistency or a permissive dev-only setting.
6. **Generated or vendored code.** Lock files, generated clients and vendored libraries, which are
   fixed upstream rather than in this diff.
7. **Logging that is already redacted.** A log call that looks like it leaks data but passes through
   a redacting logger.
8. **Style presented as a defect.** Naming, formatting or structure preferences with no failure mode.
9. **Duplicate of a finding already raised.** The same root cause reported at a second line. Merge it
   into the first row's class coverage instead.
10. **Defence in depth already present.** A missing check at one layer that another layer enforces on
    the same path. Name the other layer's line.
11. **Constant or trusted input.** An "injection" through a value that is a compile-time constant or
    comes only from trusted configuration.
12. **Out of the reviewed change.** A pre-existing defect outside the diff. Report it only if it is
    Critical; otherwise note it outside the findings table.
13. **Assumed vendor behaviour.** A defect that exists only if a vendor service behaves a certain way,
    with no fetched documentation. That is an ASSUMED row, capped at Medium, not a blocking finding.
