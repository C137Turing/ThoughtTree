"""LangGraph chat graph: load_history -> call_llm -> save_message loop."""

import os
from typing import Annotated, TypedDict
from typing_extensions import NotRequired

from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

from sqlalchemy import select
from db.mysql import async_session_factory
from models.message import Message
from models.user_config import UserConfig


class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    window_id: str
    streaming: bool
    user_message_id: NotRequired[str]
    ai_message_id: NotRequired[str]


async def _get_config() -> tuple[str, str, str | None]:
    """Returns (provider, model_name, api_key) from user_config."""
    async with async_session_factory() as session:
        result = await session.execute(
            select(UserConfig).where(UserConfig.id == 1)
        )
        config = result.scalar_one_or_none()
    model = config.active_model if config and config.active_model else "deepseek-v4-flash"
    db_key = config.api_key_encrypted if config and config.api_key_encrypted else None

    if model.startswith("gpt") or model.startswith("o1") or model.startswith("o3"):
        return "openai", model, db_key or os.getenv("OPENAI_API_KEY", "sk-xxx")
    elif model.startswith("claude"):
        return "anthropic", model, db_key or os.getenv("ANTHROPIC_API_KEY", "sk-ant-xxx")
    else:
        return "deepseek", model, db_key or os.getenv("DEEPSEEK_API_KEY", "sk-xxx")


def _get_llm(provider: str, model: str, api_key: str):
    """Create LLM instance based on provider and model."""
    if provider == "openai":
        return ChatOpenAI(
            model=model, api_key=api_key, temperature=0.7, streaming=True,
        )
    elif provider == "anthropic":
        return ChatAnthropic(
            model=model, api_key=api_key, temperature=0.7, streaming=True,
        )
    else:
        return ChatOpenAI(
            model=model, api_key=api_key,
            base_url="https://api.deepseek.com/v1",
            temperature=0.7, streaming=True,
        )


async def load_history(state: ChatState) -> ChatState:
    window_id = state["window_id"]
    messages: list[BaseMessage] = []

    async with async_session_factory() as session:
        result = await session.execute(
            select(Message)
            .where(Message.session_id == window_id)
            .order_by(Message.created_at.asc())
            .limit(40)
        )
        history = result.scalars().all()
        for msg in history:
            if msg.role == "user":
                messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                messages.append(AIMessage(content=msg.content))
            elif msg.role == "system":
                messages.append(SystemMessage(content=msg.content))

    if not messages:
        messages.append(SystemMessage(
            content=(
                "You are an AI requirements analysis assistant. "
                "Help users explore and clarify their software requirements. "
                "When you mention technical terms, explain them clearly. "
                "Use Markdown for formatting. Be concise but thorough."
            )
        ))

    return {"messages": messages, "window_id": window_id, "streaming": True}


async def call_llm(state: ChatState) -> ChatState:
    provider, model, api_key = await _get_config()
    llm = _get_llm(provider, model, api_key)
    response = await llm.ainvoke(state["messages"])
    return {
        "messages": [response],
        "window_id": state["window_id"],
        "streaming": state.get("streaming", False),
    }


async def save_message(state: ChatState) -> ChatState:
    window_id = state["window_id"]
    msgs = state["messages"]

    user_msg = None
    ai_msg = None
    for m in reversed(msgs):
        if isinstance(m, HumanMessage) and user_msg is None:
            user_msg = m
        if isinstance(m, AIMessage) and ai_msg is None:
            ai_msg = m

    async with async_session_factory() as session:
        if user_msg and not state.get("user_message_id"):
            db_msg = Message(session_id=window_id, role="user", content=user_msg.content)
            session.add(db_msg)
            await session.flush()
            state["user_message_id"] = db_msg.id

        if ai_msg and not state.get("ai_message_id"):
            db_msg = Message(session_id=window_id, role="assistant", content=ai_msg.content)
            session.add(db_msg)
            await session.flush()
            state["ai_message_id"] = db_msg.id

        await session.commit()

    return state


def build_chat_graph() -> StateGraph:
    workflow = StateGraph(ChatState)
    workflow.add_node("load_history", load_history)
    workflow.add_node("call_llm", call_llm)
    workflow.add_node("save_message", save_message)
    workflow.set_entry_point("load_history")
    workflow.add_edge("load_history", "call_llm")
    workflow.add_edge("call_llm", "save_message")
    workflow.add_edge("save_message", END)
    return workflow.compile()


chat_graph = build_chat_graph()
