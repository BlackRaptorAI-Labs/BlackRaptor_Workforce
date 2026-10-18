# Test isolation — Git in test helpers (every language)

A test that runs inside a Git hook, a rebase or another Git command inherits that command's
environment. `GIT_DIR`, `GIT_WORK_TREE` and `GIT_INDEX_FILE` then point at the REAL repository, and
every `git` call a test helper makes lands there: its `init`, its commits, its config writes. The test
passes and your own repository has changed.

## The rule

A test helper that creates a temporary Git repository:

1. builds its environment from a copy with `GIT_DIR`, `GIT_WORK_TREE`, `GIT_INDEX_FILE` and every
   `GIT_CONFIG_*` variable removed, and passes that environment and the temporary directory to every
   `git` call it makes;
2. disables hooks in that repository (`core.hooksPath` set to an empty path such as `/dev/null`);
3. unsets credential helpers for that repository (`credential.helper` set to an empty value), so a
   test can never reach a remote with your credentials.

Prove it with a fail-first test: set `GIT_DIR` to a second repository, run the helper, and assert that
the second repository has no new commit and an unchanged config. Against a helper that passes the
inherited environment through, the test must fail; only then does its pass mean anything.

## Example (Python, standard library)

```python
import hashlib, os, subprocess, tempfile, unittest

def clean_git_env():
    drop = {"GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE"}
    return {k: v for k, v in os.environ.items() if k not in drop and not k.startswith("GIT_CONFIG")}

def make_repo():
    path, env = tempfile.mkdtemp(), clean_git_env()
    def git(*args):
        subprocess.run(["git", *args], cwd=path, env=env, check=True, capture_output=True)
    git("init", "-q")
    git("config", "core.hooksPath", os.devnull)
    git("config", "credential.helper", "")
    git("-c", "user.name=t", "-c", "user.email=t", "commit", "-q", "--allow-empty", "-m", "fixture")
    return path

class HelperIsolation(unittest.TestCase):
    def test_inherited_git_dir_does_not_reach_the_real_repo(self):
        real = tempfile.mkdtemp()
        subprocess.run(["git", "init", "-q", real], check=True)
        config = os.path.join(real, ".git", "config")
        before = hashlib.sha256(open(config, "rb").read()).hexdigest()
        os.environ["GIT_DIR"] = os.path.join(real, ".git")
        try:
            make_repo()
        finally:
            del os.environ["GIT_DIR"]
        log = subprocess.run(["git", "-C", real, "log", "--oneline"], capture_output=True, text=True)
        after = hashlib.sha256(open(config, "rb").read()).hexdigest()
        print("real repo log: %r" % log.stdout)
        print("real repo config changed: %s" % (before != after))
        self.assertEqual(log.stdout, "")
        self.assertEqual(before, after)
```

The same three steps apply in any language: in Go set `cmd.Env` from a filtered `os.Environ()`, in
TypeScript pass a filtered `env` to `execFile`, in Rust call `env_remove` on the `Command`.

## Assert on full lines

A test runner may shorten long output (truncated diffs, elided strings, a summary line instead of the
detail). Never assert on output it may shorten. Print each problem on its own full line, as the
example does, and assert on that line or on the value itself.
