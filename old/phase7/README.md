# Phase 7 - Capstone Project

## Project Scope
Pick ONE business task as your capstone. Every exercise builds toward it.

### Example Topics:
- Support Triage: Automate customer support ticket routing and answers
- Document Q&A: Question answering over business documents
- Report Generator: Automated report generation from business data
- Order Lookup + Draft Reply: Look up orders and generate reply emails

## Problem Definition
- **Problem**: What manual process are you automating?
- **Current Cost**: How many hours/week does this take?
- **Success Metric**: What defines "done"? (accuracy, time saved, cost reduction)
- **Done Definition**: When is the project complete?

## Data Sources
List all data sources that will feed into the system:
- Document repositories
- Databases
- APIs
- External data feeds

## Tools Needed
- LLM provider and model
- Embedding model
- Vector store (FAISS/Chroma)
- Any custom tools (calculator, search, etc.)

## Risky Actions Needing Approval
Identify actions that require human approval:
- Email sending
- Database writes
- Payment/refund processing
- Any external API calls

## Test Set
Collect 30+ real examples as your test set:
- Factual questions
- Procedural questions
- Comparison questions
- Refusal questions (topics not in docs)

## Deployment
- Docker container
- Cheap VPS with HTTPS
- CI/CD pipeline
- Secrets management
- Backups and rollback plan

## Runbook (one page)
- What the system does
- How to deploy
- How to roll back
- What to check when it breaks
- Monthly cost
- Who to call for support

## ROI Calculation
- Hours saved × hourly cost - monthly API/VPS cost
- Track weekly: tasks handled, accuracy, approval rate, cost, time saved

## Known Limits
- Chunk size limitations
- Context window constraints
- Rate limits on API calls
- Any known failure modes

## Decision Point
After deployment, decide:
- Scale it (more users, more data)
- Fix it (improve accuracy, reduce costs)
- Pick the next system (new capstone using same stack)