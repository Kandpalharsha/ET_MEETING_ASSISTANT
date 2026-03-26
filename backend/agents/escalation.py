from state import WorkflowState, make_audit_entry


def escalation_agent(state: WorkflowState) -> WorkflowState:
    new_audit = list(state["audit_log"])

    # 🔥 retry extraction
    if state.get("current_error") == "extraction_failed":

        attempts = state.get("recovery_attempts", 0)

        if attempts < 2:
            audit = make_audit_entry(
                agent="escalation_agent",
                action="retry_extraction",
                input_summary="Extraction failed",
                output_summary=f"Retry attempt {attempts + 1}",
                reasoning="Transient error, retrying",
                status="recovery"
            )

            return {
                **state,
                "audit_log": new_audit + [audit],
                "current_error": None,
                "recovery_attempts": attempts + 1
            }

        # escalate after retries
        audit = make_audit_entry(
            agent="escalation_agent",
            action="escalated_to_human",
            input_summary="Extraction failed",
            output_summary="Human intervention required",
            reasoning="Max retries reached",
            status="escalated"
        )

        return {
            **state,
            "audit_log": new_audit + [audit]
        }

    return state