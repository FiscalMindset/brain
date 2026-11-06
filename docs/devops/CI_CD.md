# CI/CD
`.github/workflows/ci.yml`: Python 3.13 → pip install → pytest with `--cov-fail-under=30`; Node 20 → npm install → build. Docker workflow builds images (no push by default).
