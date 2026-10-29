# ZEVQ KeepAlive

Minimal bronze-and-charcoal dashboard for Render service health monitoring.

## Development

Run `npm install` and `npm run dev`. Build with `npm run build`.

## Deployment

Deploy to Vercel as a Vite project. Monitoring in this initial release is **not connected to the UI**. The GitHub Actions sample workflow is a separate scheduled health-check mechanism. Do not assume 24/7 guaranteed availability; GitHub scheduled jobs can run late and Render may still restart services.

## Security

Do not put secret internal endpoints or credentials in public configuration. Do not use the browser dashboard as proof that a service is healthy until actual checks are connected.
