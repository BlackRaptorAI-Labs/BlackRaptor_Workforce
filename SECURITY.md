# Security policy

## How to report

Report security problems privately through GitHub: open the **Security** tab of this repository and
choose **Report a vulnerability**. Do not open a public issue for a security problem.

## What counts

- A hook that fails open: a check that should block work lets it through when it errors, times
  out, or is missing a file.
- A review gate that can be bypassed: a way to get a passing verdict recorded without the gate
  having judged the work.
- A leak of private paths or private content into the shipped files.

Problems in Claude Code itself go to Anthropic, not here.

## What to expect

We acknowledge a report within 5 business days and tell you whether we accept it. If we accept it,
we fix it in a release and credit you in the changelog unless you ask us not to.
