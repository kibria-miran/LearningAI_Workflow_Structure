================================================================
PHASE 7 - PROJECT STRUCTURE (CAPSTONE, NO NEW LEARNING)
================================================================

phase7/
├── README.md               <- scope template + weekly results table
├── CAPSTONE_SCOPE.md       <- you write this in Week 1
├── runbook.md              <- one page: deploy, rollback, debug, cost
├── config.json             <- reference values (nothing reads it by default)
├── week1_scope.txt
├── week2_build_v1.txt
├── week3_harden.txt
├── week4_deploy.txt
├── week5_monitor_measure.txt
└── week6_document_decide.txt

The capstone CODE lives in your own repo/folder and reuses
phase3 (tracker), phase4 (RAG), phase5 (agent + guardrails),
phase6 (Docker, VPS, CI/CD). Do not learn new tools here.

config.json is a reference for the values you chose. Your code must
load it (json.load) before it has any effect.
================================================================
