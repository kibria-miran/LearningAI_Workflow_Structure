# Capstone Runbook

## System Overview
[Description of what this system does]

## Deployment Instructions
1. Prerequisites: [list requirements]
2. Docker: `docker pull [image]` or `docker-compose up -d`
3. VPS: SSH into [server], run deployment commands
4. HTTPS: [Caddy/Nginx configuration]
5. Secrets: [how secrets are managed]

## Rollback Procedure
1. Stop current container: `docker stop [container]`
2. Roll back to previous version: `docker pull [previous-image]`
3. Restart: `docker start [container]`

## Monitoring Checklist (daily)
- [ ] Uptime check
- [ ] Error alerts
- [ ] Cost dashboard - daily spend
- [ ] API rate limit warnings
- [ ] Backup status

## Monthly Cost Review
- API costs: $[amount]
- VPS costs: $[amount]
- Total monthly: $[amount]
- ROI: [hours saved × rate] - total costs

## Escalation Contacts
- Primary: [name/email]
- Secondary: [name/email]
- VPS provider: [support link]

## Known Issues & Workarounds
1. [Issue 1] → [Workaround]
2. [Issue 2] → [Workaround]