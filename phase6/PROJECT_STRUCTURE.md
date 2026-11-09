================================================================
PHASE 6 - PROJECT STRUCTURE (SHIP IT)
================================================================

Phase 6 runs in parallel with Phases 3-5. It needs this layout:

  ai-roadmap/
  ├── phase3/   tracker.py, config/, ...      (copied into the image)
  ├── phase4/   data/, build_index.py, ask.py, src/   (copied into the image)
  └── phase6/
      ├── app.py                  <- FastAPI: /, /health, POST /query
      ├── start.sh                <- builds index if needed, starts uvicorn
      ├── Dockerfile              <- build context = parent folder
      ├── Dockerfile.dockerignore <- keeps .env, venv, other phases out
      ├── docker-compose.yml      <- rag-app + n8n, named volumes
      ├── requirements.txt
      ├── .env.example / .gitignore
      ├── stage_a_secrets_budget.txt
      ├── stage_b_docker_n8n.txt
      ├── stage_c_vps_cicd.txt
      ├── stage_d_reliability.txt
      └── stage_e_runbook.txt

QUICK REFERENCE
  cd phase6 && cp .env.example .env
  docker compose up -d --build
  docker compose logs -f rag-app
  curl localhost:8000/health
  docker compose down            # keeps volumes
  docker compose down -v         # DELETES volumes (index, n8n data)

POST /query
  header: X-API-Key: <APP_API_KEY>
  body  : {"question": "..."}
  reply : {"answer","sources","refused","cost"}   (refusal = 200, refused=true)
================================================================
