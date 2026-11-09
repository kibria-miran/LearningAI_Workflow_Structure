# Capstone Runbook  (fill every [bracket]; keep to one page)

## What it does
[one paragraph: task, users, inputs, outputs]

## Deploy
1. Prerequisites: [server, domain, Docker]
2. On the server: `cd ~/ai-roadmap && git pull && cd phase6 && docker compose up -d --build`
3. HTTPS: [Caddy config location]
4. Secrets: `.env` on the server only, never in git or the image

## Roll back
1. `git tag` shows releases; find the last good one: [vX.Y.Z]
2. `git checkout [vX.Y.Z] && cd phase6 && docker compose up -d --build`
3. Verify: `curl https://[domain]/health`

## When it breaks, check in order
1. `curl https://[domain]/health`
2. `docker compose logs --tail=100 rag-app`
3. Provider status page + budget cap hit? (`results/usage.jsonl`)
4. Disk space, memory (`df -h`, `free -m`)
5. Last deploy: did the pipeline run? Roll back if unsure.

## Backups
[what, where, how often, last restore test date]

## Monthly cost
API $[ ] + VPS $[ ] = $[ ]    Hours saved [ ] x $[ ]/h  ->  ROI $[ ]

## Contacts
Primary: [name/phone]   Backup: [name/phone]   VPS support: [link]

## Known limits
1. [limit] -> [workaround]
