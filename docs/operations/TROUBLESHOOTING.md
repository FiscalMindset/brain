# Troubleshooting

| Symptom | Fix |
| Agent doesn't answer in Switch room | Check `@` spelling matches agent name exactly; ensure session attending (Switch Console shows room claimed) |
| 401 everywhere | Re-login; token expired (24h) or `SECRET_KEY` changed |
| Upload 400 | Check extension (.pdf/.md/.txt), ≤5 files, ≤2MB |
| Search misses | Try single terms; empty query returns latest docs |
| `npm run build` vite not found | Run `npm install` first |
