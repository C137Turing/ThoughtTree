"""Quality check graph: completeness, consistency, testability, EARS compliance."""

import re
from typing import TypedDict, NotRequired

from sqlalchemy import select
from db.mysql import async_session_factory
from models.session import Session
from models.message import Message
from models.session_tree import SessionTree


class QualityState(TypedDict):
    root_id: str
    nodes: NotRequired[list[dict]]
    report: NotRequired[dict]


async def traverse_tree(state: QualityState) -> QualityState:
    root_id = state["root_id"]
    nodes = []
    async with async_session_factory() as session:
        result = await session.execute(
            select(Session, SessionTree.depth)
            .join(SessionTree, Session.id == SessionTree.descendant_id)
            .where(SessionTree.ancestor_id == root_id)
            .order_by(SessionTree.depth)
        )
        for row in result.all():
            s = row[0]
            depth = row[1]
            msg_result = await session.execute(
                select(Message)
                .where(Message.session_id == s.id)
                .order_by(Message.created_at.desc())
                .limit(1)
            )
            last_msg = msg_result.scalar_one_or_none()
            nodes.append({
                "id": s.id, "title": s.title, "depth": depth,
                "status": s.status,
                "description": last_msg.content if last_msg else "",
            })
    state["nodes"] = nodes
    return state


async def check_completeness(state: QualityState) -> QualityState:
    nodes = state["nodes"]
    issues = []
    for node in nodes:
        has_children = any(
            n["depth"] == node["depth"] + 1 and n.get("parent_id") == node["id"]
            for n in nodes
        )
        if not has_children and node["status"] == "open" and not node["description"]:
            issues.append({
                "type": "completeness", "severity": "warning",
                "node_id": node["id"], "title": node["title"],
                "message": 'Node "' + node["title"] + '" has no AI response.',
            })
    state["report"] = state.get("report", {})
    state["report"]["completeness"] = {
        "passed": len(issues) == 0,
        "total_nodes": len(nodes),
        "issues": issues,
        "summary": "All leaf nodes have responses." if len(issues) == 0
        else str(len(issues)) + " leaf node(s) unanswered.",
    }
    return state


async def check_consistency(state: QualityState) -> QualityState:
    nodes = state["nodes"]
    issues = []
    conflict_groups = [
        ["PayPal", "Stripe"],
        ["REST", "GraphQL"],
        ["MongoDB", "PostgreSQL", "MySQL"],
        ["React", "Vue", "Angular"],
        ["AWS", "GCP", "Azure"],
        ["monolith", "microservices"],
        ["SQL", "NoSQL"],
        ["sync", "async"],
        ["on-premise", "cloud"],
    ]
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            t1 = (nodes[i]["title"] + " " + nodes[i]["description"]).lower()
            t2 = (nodes[j]["title"] + " " + nodes[j]["description"]).lower()
            for group in conflict_groups:
                found_a = next((k for k in group if k.lower() in t1), None)
                found_b = next((k for k in group if k.lower() in t2), None)
                if found_a and found_b and found_a != found_b:
                    issues.append({
                        "type": "consistency", "severity": "warning",
                        "node_a": nodes[i]["title"], "node_b": nodes[j]["title"],
                        "term_a": found_a, "term_b": found_b,
                        "message": "Conflict: " + found_a + " vs " + found_b,
                    })
    state["report"]["consistency"] = {
        "passed": len(issues) == 0, "issues": issues,
        "summary": "No conflicts." if len(issues) == 0
        else str(len(issues)) + " conflict(s) found.",
    }
    return state


async def check_testability(state: QualityState) -> QualityState:
    nodes = state["nodes"]
    vague_terms = ["fast", "quick", "friendly", "efficient", "various", "some",
                   "smooth", "good-looking", "stable", "beautiful", "nice",
                   "robust", "scalable", "flexible", "easy", "simple"]
    issues = []
    for node in nodes:
        if not node["description"]:
            continue
        found = [t for t in vague_terms if t in node["description"].lower()]
        if found:
            issues.append({
                "type": "testability", "severity": "info",
                "node_id": node["id"], "title": node["title"],
                "terms": found,
                "message": "Vague terms: " + ", ".join(found) + ". Quantify.",
            })
    state["report"]["testability"] = {
        "passed": len(issues) == 0, "issues": issues,
        "summary": "All measurable." if len(issues) == 0
        else str(len(issues)) + " node(s) with vague terms.",
    }
    return state


async def check_ears(state: QualityState) -> QualityState:
    nodes = state["nodes"]
    fn = [n for n in nodes if n["depth"] > 0 and n["description"]]
    total = len(fn)
    ears_re = re.compile(
        r'(When|If|当|如果)\s+.*?(the system shall|the\s+\w+\s+shall|系统应|应)',
        re.IGNORECASE,
    )
    compliant = sum(1 for n in fn if ears_re.search(n["description"]))
    rate = round(compliant / total * 100) if total > 0 else 100
    state["report"]["ears"] = {
        "passed": rate >= 80, "rate": rate,
        "compliant": compliant, "total": total,
        "summary": "EARS: " + str(rate) + "% (" + str(compliant) + "/" + str(total) + ").",
    }
    return state


async def aggregate_report(state: QualityState) -> QualityState:
    report = state["report"]
    all_passed = all(
        report.get(k, {}).get("passed", False)
        for k in ["completeness", "consistency", "testability", "ears"]
    )
    report["overall"] = {
        "passed": all_passed,
        "summary": "All checks passed." if all_passed
        else "Issues found. Review before generating SDD.",
    }
    state["report"] = report
    return state


async def run_quality_check(root_id: str) -> dict:
    state: QualityState = {"root_id": root_id, "report": {}}
    state = await traverse_tree(state)
    state = await check_completeness(state)
    state = await check_consistency(state)
    state = await check_testability(state)
    state = await check_ears(state)
    state = await aggregate_report(state)
    return state["report"]