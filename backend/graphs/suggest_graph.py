from sqlalchemy import select
from db.mysql import async_session_factory
from models.session import Session
from models.message import Message
from models.session_tree import SessionTree

async def generate_suggestions(root_id: str) -> dict:
    suggestions = []
    nodes = []
    async with async_session_factory() as session:
        result = await session.execute(
            select(Session, SessionTree.depth)
            .join(SessionTree, Session.id == SessionTree.descendant_id)
            .where(SessionTree.ancestor_id == root_id)
            .order_by(SessionTree.depth)
        )
        for row in result.all():
            s = row[0]; depth = row[1]
            msg_result = await session.execute(
                select(Message).where(Message.session_id == s.id)
                .order_by(Message.created_at.desc()).limit(1)
            )
            last_msg = msg_result.scalar_one_or_none()
            nodes.append({"id": s.id, "title": s.title, "depth": depth,
                         "status": s.status,
                         "description": last_msg.content if last_msg else ""})

    known = {
        "auth": ["auth","login","signup","oauth","jwt"],
        "data storage": ["database","sql","nosql","mongodb","redis"],
        "error handling": ["error","exception","fallback","retry"],
        "logging": ["log","monitoring","observability","tracing"],
        "testing": ["test","unit test","integration","e2e"],
        "deployment": ["deploy","docker","kubernetes","ci/cd"],
        "security": ["security","encryption","ssl","tls","xss"],
        "api design": ["api","rest","graphql","endpoint","swagger"],
        "performance": ["performance","caching","latency","throughput"],
        "accessibility": ["accessibility","a11y","wcag"],
    }
    all_text = " ".join(n["title"] + " " + n["description"] for n in nodes).lower()
    for dim_name, keywords in known.items():
        if not any(kw.lower() in all_text for kw in keywords):
            suggestions.append({
                "type": "missing_dimension", "dimension": dim_name,
                "message": "Consider exploring: " + dim_name,
                "action": "analyze",
            })

    dangling = [n for n in nodes if n["status"] == "open"
                and not n["description"] and n["depth"] > 0]
    if dangling:
        suggestions.append({
            "type": "dangling_nodes", "count": len(dangling),
            "nodes": [{"id": n["id"], "title": n["title"]} for n in dangling[:5]],
            "message": str(len(dangling)) + " unanswered node(s) need attention.",
            "action": "review",
        })

    return {
        "suggestions": suggestions,
        "stats": {
            "total_nodes": len(nodes),
            "answered": sum(1 for n in nodes if n["description"]),
            "closed": sum(1 for n in nodes if n["status"] == "closed"),
            "dangling": len(dangling),
        },
    }