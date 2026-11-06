# Agent Architecture
9 agents in `apps/api/app/services/agents.py`. Orchestrator chain: research → knowledge → reviewer → verifier → learning → memory → qa → project-manager. Each returns structured dicts with `human_approval`. Failures are explicit (gaps/issues, blocked verdicts), never silent. Switch-side agents mirror this chain in `switch/agents/`.
