# Submission Checklist

- [ ] `docker compose config` clean; `docker compose up` boots api+web.
- [ ] `cd apps/api && .venv/bin/python -m pytest -q` → 46 passed.
- [ ] `cd apps/web && npm install && npm run build` → clean.
- [ ] Switch Console: import `switch/secondbrain-room.template.yaml`, `@secondbrain-researcher` answers with citations.
- [ ] README Switch section + architecture diagram present.
- [ ] Demo script rehearsed; video ≤3 min.
- [ ] No secrets in repo (`git status` clean of `.env`/`*.db`).
