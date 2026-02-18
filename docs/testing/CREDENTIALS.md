## Test Credentials — Secure CI usage

This file describes how CI should provide test credentials for running automated tests.

Recommended approach

- Keep `tests/fixtures/credentials.py` out of source control. Instead, populate it during CI runs.
- Use the helper script `dev/ci/generate_test_credentials.py` which reads environment variables listed below and writes `tests/fixtures/credentials.py`.
- Add the corresponding secrets in your CI provider (GitHub Secrets, Vault, etc.).

Common env variable names (examples):

- `TEST_ADMIN_PASSWORD`
- `TEST_PASSWORD`
- `TEST_API_KEY`
- `ADMIN_PASSWORD`
- `API_KEY`

Usage in GitHub Actions

1. Add the required secrets in `Settings -> Secrets`.
2. Use the provided workflow `.github/workflows/generate-test-creds.yml` as a reference step.
3. Download the artifact in your test job or run the generator script directly before tests.

Example step to download artifact in another workflow:

```yaml
- name: Download test credentials artifact
  uses: actions/download-artifact@v3
  with:
    name: test-credentials

- name: Move credentials into place
  run: |
    mkdir -p tests/fixtures
    mv test-credentials tests/fixtures/credentials.py
```

Security notes

- Never commit `tests/fixtures/credentials.py` to VCS.
- Rotate test secrets regularly and use short-lived secrets where possible.
