from datetime import datetime
from state import WorkflowState, make_audit_entry
from mock.task_board import task_board


def task_creation_agent(state: WorkflowState) -> WorkflowState:
    """
    Creates task cards with intelligent decision-making:

    - High confidence → create task
    - Medium confidence → create but flag
    - Low confidence → escalate (skip)

    Includes duplicate detection and full audit reasoning.
    """
    new_audit      = list(state["audit_log"])
    tasks_created  = list(state["tasks_created"])
    failed_tasks   = list(state["failed_tasks"])

    # 🔥 NEW: agent thinking
    new_audit.append(make_audit_entry(
        agent="task_creation_agent",
        action="task_planning_started",
        input_summary=f"{len(state['action_items'])} items",
        output_summary="Evaluating tasks for creation",
        reasoning="[STEP] Validate ownership → check duplicates → apply confidence rules",
        status="success",
    ))

    for item in state["action_items"]:
        desc = item["description"][:60]
        confidence = item["owner_confidence"]

        # ── SKIP: escalated items ─────────────────────────────────────
        if item["status"] == "escalated":
            new_audit.append(make_audit_entry(
                agent="task_creation_agent",
                action="task_skipped_awaiting_owner",
                input_summary=desc,
                output_summary="Skipped — owner unresolved",
                reasoning=(
                    "[DECISION] No confirmed owner → "
                    "[ACTION] Hold task → avoid misassignment"
                ),
                status="recovery",
            ))
            continue

        # ── 🔥 NEW: LOW CONFIDENCE → ESCALATE ─────────────────────────
        if confidence < 0.6:
            item["status"] = "escalated"

            new_audit.append(make_audit_entry(
                agent="task_creation_agent",
                action="task_escalated_low_confidence",
                input_summary=desc,
                output_summary="Escalated — owner confidence too low",
                reasoning=(
                    f"[DECISION] Confidence {confidence:.0%} < 60% → "
                    "[ACTION] escalate to human → "
                    "[RISK] avoid incorrect assignment"
                ),
                status="escalated",
            ))
            continue

        # ── DUPLICATE CHECK ──────────────────────────────────────────
        if task_board.exists(item["description"]):
            failed_tasks.append({
                "item_id": item["id"],
                "reason": "duplicate_task",
                "description": desc,
            })

            new_audit.append(make_audit_entry(
                agent="task_creation_agent",
                action="task_skipped_duplicate",
                input_summary=desc,
                output_summary="Duplicate — not created",
                reasoning=(
                    "[DECISION] Task already exists → "
                    "[ACTION] skip duplicate → maintain clean board"
                ),
                status="recovery",
            ))
            continue

        # ── CREATE TASK ──────────────────────────────────────────────
        try:
            task_id = task_board.create({
                "id": item["id"],
                "title": item["description"],
                "owner": item["owner"],
                "deadline": item["deadline"],
                "priority": item["priority"],
                "category": item.get("category", "editorial"),
                "status": "pending",
                "nudge_sent": False,
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
            })

            tasks_created.append(task_id)

            # 🔥 NEW: differentiate confidence levels
            if confidence < 0.8:
                status = "recovery"
                note = " (needs review)"
            else:
                status = "success"
                note = ""

            new_audit.append(make_audit_entry(
                agent="task_creation_agent",
                action="task_created",
                input_summary=desc,
                output_summary=(
                    f"Task {task_id} → {item['owner']} · "
                    f"Due {item['deadline']}{note}"
                ),
                reasoning=(
                    f"[DECISION] Confidence {confidence:.0%} → "
                    f"[ACTION] create task → "
                    f"[RESULT] assigned to {item['owner']} → "
                    f"Slack notification sent (simulated)"
                ),
                status=status,
            ))

        except Exception as e:
            failed_tasks.append({
                "item_id": item["id"],
                "reason": str(e),
                "description": desc,
            })

            new_audit.append(make_audit_entry(
                agent="task_creation_agent",
                action="task_creation_failed",
                input_summary=desc,
                output_summary="Creation error",
                reasoning=f"[ERROR] Task board failure → {str(e)}",
                status="failure",
            ))

    return {
        **state,
        "tasks_created": tasks_created,
        "failed_tasks": failed_tasks,
        "audit_log": new_audit,
    }