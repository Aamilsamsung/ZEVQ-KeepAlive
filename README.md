# ZEVQ KeepAlive

Minimal monitoring dashboard for public Render endpoints.

**Live frontend:** https://zevq-keepalive.vercel.app

## Architecture
- `monitors.json`: authoritative list of public Render HTTPS endpoints.
- `scripts/check.py`: makes real HTTP requests, records status, latency and timestamp.
- `.github/workflows/monitor.yml`: scheduled check every 10 minutes and manual trigger; writes `status.json`.
- `status.json`: public snapshot/history, updated only after the checker successfully runs.
- Vite frontend: reads public snapshot from GitHub; browser-side service edits are local-only and do **not** change the checker.

## Complete GitHub Actions setup
1. Open repository Settings → Actions → General.
2. Under **Workflow permissions**, choose **Read and write permissions**, and save.
3. Open **Actions → Monitor Render services → Run workflow**.
4. Verify a successful run, a new `status.json` commit, and the resulting dashboard statuses.
5. For new services, edit `monitors.json` in GitHub (the dashboard editor is local-only).

GitHub scheduled jobs are best-effort and may be delayed or skipped. Requests do not guarantee continuous uptime or bypass Render limits. The app cannot claim 24/7 availability. For reliable monitoring use a dedicated paid worker/scheduler.

## Security and limitations
The repository and `status.json` are public. Only add public non-sensitive URLs. The checker restricts URLs to HTTPS `*.onrender.com` and disallows redirects to other hosts. Browser storage is not authenticated or shared. No notifications, authenticated admin panel, or backend database are implemented yet. The initial uptime percentage is only a ratio of recorded checks, not a full historical SLA.

## Development
`npm install && npm run dev`
`npm run build`
`python3 scripts/check.py` runs a check locally and updates `status.json`.
