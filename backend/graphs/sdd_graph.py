"""SDD generation graph: traverse_tree -> classify_nodes -> map_to_ieee830 -> generate_sections -> assemble_sdd."""

import uuid
from datetime import datetime
from typing import TypedDict, NotRequired

from sqlalchemy import select
from db.mysql import async_session_factory
from models.session import Session
from models.message import Message
from models.session_tree import SessionTree
from models.user_config import UserConfig


class SddState(TypedDict):
    root_id: str
    nodes: NotRequired[list[dict]]
    sections: NotRequired[dict]
    sdd_markdown: NotRequired[str]


async def _get_config() -> dict:
    async with async_session_factory() as session:
        result = await session.execute(select(UserConfig).where(UserConfig.id == 1))
        config = result.scalar_one_or_none()
    return {
        "ears_enabled": config.ears_enabled if config else False,
        "numbering_style": config.numbering_style if config else "standard",
        "mapping_rules": config.sdd_mapping_rules if config else None,
    }


async def traverse_tree(state: SddState) -> SddState:
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
            description = last_msg.content[:200] if last_msg else ""
            nodes.append({
                "id": s.id, "title": s.title, "parent_id": s.parent_id,
                "depth": depth, "status": s.status, "description": description,
            })
    state["nodes"] = nodes
    return state


async def classify_nodes(state: SddState) -> SddState:
    nodes = state["nodes"]
    for node in nodes:
        title = (node["title"] or "").lower()
        desc = (node["description"] or "").lower()
        combined = title + " " + desc
        if node["status"] == "closed" or not node["description"]:
            node["classification"] = "unresolved"
        elif any(kw in combined for kw in ["performance", "security", "safety", "availability", "reliability"]):
            node["classification"] = "non_functional"
        elif any(kw in combined for kw in ["api", "payment", "sdk", "integration", "interface"]):
            node["classification"] = "external"
        else:
            node["classification"] = "functional"
    state["nodes"] = nodes
    return state


async def map_to_ieee830(state: SddState) -> SddState:
    config = await _get_config()
    nodes = state["nodes"]
    sections = {
        "introduction": {"title": "1. Introduction", "items": []},
        "functional": {"title": "2. Functional Requirements", "items": []},
        "non_functional": {"title": "3. Non-Functional Requirements", "items": []},
        "external": {"title": "4. External Interfaces", "items": []},
        "appendix": {"title": "Appendix: Pending Items", "items": []},
    }
    for node in nodes:
        if node["depth"] == 0:
            sections["introduction"]["items"].append(node)
        elif node["classification"] == "unresolved":
            sections["appendix"]["items"].append(node)
        elif node["classification"] == "non_functional":
            sections["non_functional"]["items"].append(node)
        elif node["classification"] == "external":
            sections["external"]["items"].append(node)
        else:
            sections["functional"]["items"].append(node)
    state["sections"] = sections
    return state


def _numbering_standard(index: list[int]) -> str:
    return ".".join(str(i) for i in index)


def _numbering_chinese(index: list[int]) -> str:
    if len(index) == 1:
        chars = ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"]
        return chars[index[0] - 1] if index[0] <= 10 else str(index[0])
    elif len(index) == 2:
        return str(index[1]) + "."
    return "(" + str(index[0]) + ")"


async def generate_sections(state: SddState) -> SddState:
    config = await _get_config()
    numbering = config["numbering_style"] or "standard"
    ears = config["ears_enabled"] or False
    sections = state["sections"]
    md = "# Software Design Document\n\n"
    section_order = ["introduction", "functional", "non_functional", "external", "appendix"]

    for key in section_order:
        section = sections.get(key)
        if not section or not section["items"]:
            continue
        md += "## " + section["title"] + "\n\n"
        for i, item in enumerate(section["items"]):
            if numbering == "chinese":
                num = _numbering_chinese([i + 1])
            else:
                num = _numbering_standard([i + 1])
            md += "### " + num + " " + item["title"] + "\n\n"
            if item["description"]:
                desc = item["description"]
                if ears and item["classification"] == "functional":
                    if "When" not in desc and "shall" not in desc:
                        desc = "**EARS**: When the system receives " + item["title"] + ", it shall process the request accordingly.\n\n" + desc
                md += desc + "\n\n"
            if item["status"] == "closed":
                md += "> Status: Closed\n\n"

    state["sdd_markdown"] = md
    return state


async def assemble_sdd(state: SddState) -> SddState:
    md = state["sdd_markdown"] or ""
    md = "*Generated: " + datetime.now().strftime("%Y-%m-%d %H:%M") + "*\n\n" + md
    state["sdd_markdown"] = md
    return state


_tasks: dict[str, dict] = {}


async def generate_sdd(root_id: str) -> str:
    task_id = str(uuid.uuid4())
    _tasks[task_id] = {"status": "processing", "sdd": None}
    state: SddState = {"root_id": root_id}
    try:
        state = await traverse_tree(state)
        state = await classify_nodes(state)
        state = await map_to_ieee830(state)
        state = await generate_sections(state)
        state = await assemble_sdd(state)
        _tasks[task_id] = {"status": "done", "sdd": state["sdd_markdown"]}
    except Exception as e:
        _tasks[task_id] = {"status": "error", "sdd": str(e)}
    return task_id


def get_task(task_id: str) -> dict | None:
    return _tasks.get(task_id)