"""In-process multi-agent orchestration."""
from __future__ import annotations

from app.services.retrieval import citation_for, search_documents

AGENTS = [
 {"name": "orchestrator", "role": "Plans work, delegates.", "permissions": ["delegate", "run", "read"]},
 {"name": "research", "role": "Retrieves evidence.", "permissions": ["read", "search"]},
 {"name": "knowledge", "role": "Extracts entities and relationships.", "permissions": ["read", "write"]},
 {"name": "learning", "role": "Distils durable facts into long-term user memory.", "permissions": ["read", "write"]},
 {"name": "project-manager", "role": "Turns findings into projects and tasks.", "permissions": ["read", "write"]},
 {"name": "reviewer", "role": "Checks evidence coverage.", "permissions": ["read"]},
 {"name": "memory", "role": "Reads and writes user-scoped memory.", "permissions": ["read", "write"]},
 {"name": "verifier", "role": "Validates citations resolve to real documents.", "permissions": ["read"]},
 {"name": "qa", "role": "Generates follow-up checks and quality questions.", "permissions": ["read"]},
]
AGENT_NAMES = [a["name"] for a in AGENTS]

def run_research_agent(db, user_id, query, *, limit=10):
    docs = search_documents(db, user_id, query, limit=limit)
    return {"agent": "research", "findings": [{"text": d.text[:400], "document_id": d.id, "chunk_index": d.chunk_index} for d in docs], "evidence_count": len(docs), "citations": [citation_for(d) for d in docs], "gaps": ["No evidence found; ingest more sources."] if not docs else [], "contradictions": [], "human_approval": True}

def _get_or_create_entity(db, user_id, name, kind="term"):
    from app.models.models import KnowledgeEntity
    existing = db.query(KnowledgeEntity).filter(KnowledgeEntity.user_id == user_id, KnowledgeEntity.name == name).first()
    if existing: return existing
    e = KnowledgeEntity(user_id=user_id, name=name, kind=kind)
    db.add(e); db.flush()
    return e

def run_knowledge_agent(db, user_id, query, research):
    from app.models.models import KnowledgeRelationship
    entities, rels, seen = [], [], set()
    for finding in research.get("findings", []):
        # entities from this finding
        finding_entities = []
        for word in finding["text"].split():
            clean = word.strip(",.:;!?()\"'").lower()
            if len(clean) > 5 and clean.isalpha() and clean not in seen:
                seen.add(clean)
                e = _get_or_create_entity(db, user_id, clean)
                entity_rec = {"id": e.id, "name": clean}
                if entity_rec not in entities: entities.append(entity_rec)
                finding_entities.append(e)
                if len(entities) >= 20: break
        # co-occurrence relationships within same finding
        for i in range(len(finding_entities)):
            for j in range(i+1, len(finding_entities)):
                a, b = finding_entities[i], finding_entities[j]
                if (a.id, b.id) in {(r["source_entity_id"], r["target_entity_id"]) for r in rels}: continue
                # avoid duplicate rel rows
                dup = db.query(KnowledgeRelationship).filter(KnowledgeRelationship.user_id == user_id, KnowledgeRelationship.source_entity_id == a.id, KnowledgeRelationship.target_entity_id == b.id, KnowledgeRelationship.relation == "co-occurs").first()
                if dup:
                    rels.append({"id": dup.id, "source_entity_id": a.id, "target_entity_id": b.id, "relation": "co-occurs"})
                    continue
                rel = KnowledgeRelationship(user_id=user_id, source_entity_id=a.id, target_entity_id=b.id, relation="co-occurs")
                db.add(rel); db.flush()
                rels.append({"id": rel.id, "source_entity_id": a.id, "target_entity_id": b.id, "relation": "co-occurs"})
        if len(entities) >= 20: break
    return {"agent": "knowledge", "entities": entities, "relationships": rels, "human_approval": True}

def run_reviewer_agent(research):
    issues = []
    if research.get("evidence_count", 0) == 0: issues.append("No evidence retrieved for this query.")
    elif research["evidence_count"] < 2: issues.append("Single source only; corroborate before acting.")
    return {"agent": "reviewer", "approved": not issues, "issues": issues, "contradictions": research.get("contradictions", []), "human_approval": True}

def run_verifier_agent(db, user_id, research):
    from app.models.models import Document
    verified = []
    for c in research.get("citations", []):
        exists = db.query(Document).filter(Document.id == c.get("document_id")).first() is not None
        verified.append({**c, "verified": exists})
    return {"agent": "verifier", "checked": len(verified), "verified": sum(1 for v in verified if v["verified"]), "citations": verified, "human_approval": True}

def run_learning_agent(db, user_id, query, research):
    from app.models.models import UserMemory
    created = []
    for idx, f in enumerate(research.get("findings", [])[:5]):
        key = f"learned:{query[:40]}:{idx}"
        existing = db.query(UserMemory).filter(UserMemory.user_id == user_id, UserMemory.key == key).first()
        if existing:
            created.append({"id": existing.id, "key": existing.key}); continue
        m = UserMemory(user_id=user_id, key=key, value=f["text"][:500], meta={"source_document_id": f.get("document_id"), "query": query})
        db.add(m); db.flush()
        created.append({"id": m.id, "key": m.key})
    return {"agent": "learning", "created_memories": created, "human_approval": True}

def run_memory_agent(db, user_id, research=None):
    from app.models.models import UserMemory
    memories = db.query(UserMemory).filter(UserMemory.user_id == user_id).all()
    return {"agent": "memory", "count": len(memories), "memories": [{"id": m.id, "key": m.key, "value": m.value} for m in memories], "human_approval": True}

def run_qa_agent(research, reviewer=None):
    questions = []
    if research.get("evidence_count", 0) == 0: questions.append("What other sources should be ingested?")
    if reviewer and reviewer.get("issues"):
        for issue in reviewer["issues"]:
            questions.append(f"How to address: {issue}")
    if not questions and research.get("findings"): questions.append("Can this finding be corroborated by another source?")
    return {"agent": "qa", "questions": questions, "human_approval": True}

def run_project_manager_agent(db, user_id, query, research):
    from app.models.models import Project, ProjectTask
    project = Project(user_id=user_id, title=f"Research: {query}"[:512], description=query)
    db.add(project); db.flush()
    tasks = []
    for finding in research.get("findings", [])[:5]:
        task = ProjectTask(project_id=project.id, title=f"Review: {finding['text'][:80]}", body=finding["text"])
        db.add(task); db.flush()
        tasks.append({"id": task.id, "title": task.title})
    return {"agent": "project-manager", "project_id": project.id, "tasks": tasks, "human_approval": True}

def run_orchestration(db, user_id, query):
    from app.models.models import AgentExecution
    research = run_research_agent(db, user_id, query)
    knowledge = run_knowledge_agent(db, user_id, query, research)
    reviewer = run_reviewer_agent(research)
    verifier = run_verifier_agent(db, user_id, research)
    learning = run_learning_agent(db, user_id, query, research)
    memory = run_memory_agent(db, user_id, research)
    qa = run_qa_agent(research, reviewer)
    project = run_project_manager_agent(db, user_id, query, research)
    output = {"query": query, "steps": [research, knowledge, reviewer, verifier, learning, memory, qa, project], "findings": research["findings"], "contradictions": research["contradictions"], "gaps": research["gaps"] + reviewer["issues"], "citations": research["citations"], "verifier": verifier, "qa": qa, "project_id": project["project_id"], "human_approval": True, "next_actions": ["Review the draft project and tasks.", "Approve entities before merging into the knowledge graph."]}
    db.add(AgentExecution(user_id=user_id, agent_name="orchestrator", input={"query": query}, output=output)); db.flush()
    return output
