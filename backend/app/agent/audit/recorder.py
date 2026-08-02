import hashlib
import json
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from ..schemas.tool_result import ToolResultSchema


class AuditRecorder:
    def __init__(self, db_session_factory):
        self.db_session_factory = db_session_factory

    def record_tool_execution(
        self,
        session_id: str,
        agent_id: str,
        tool_name: str,
        parameters: Dict[str, Any],
        result: ToolResultSchema,
        duration_ms: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        input_str = json.dumps(parameters, sort_keys=True, default=str)
        input_hash = hashlib.sha256(input_str.encode()).hexdigest()

        timestamp = datetime.now(timezone.utc).isoformat()

        try:
            with self.db_session_factory() as db:
                db.execute(
                    """
                    INSERT INTO agent_audit_logs 
                    (session_id, agent_id, tool_name, input_hash, output_status, result_ref, duration_ms, timestamp, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        session_id,
                        agent_id,
                        tool_name,
                        input_hash,
                        result.status,
                        json.dumps(result.to_dict(), default=str),
                        duration_ms,
                        timestamp,
                        json.dumps(metadata or {}, default=str),
                    ),
                )
                db.commit()
        except Exception:
            pass

    def record_agent_action(
        self,
        session_id: str,
        agent_id: str,
        action: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        duration_ms: Optional[int] = None,
    ) -> None:
        input_str = json.dumps(input_data, sort_keys=True, default=str)
        input_hash = hashlib.sha256(input_str.encode()).hexdigest()

        timestamp = datetime.now(timezone.utc).isoformat()

        try:
            with self.db_session_factory() as db:
                db.execute(
                    """
                    INSERT INTO agent_audit_logs 
                    (session_id, agent_id, tool_name, input_hash, output_status, result_ref, duration_ms, timestamp, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        session_id,
                        agent_id,
                        action,
                        input_hash,
                        "success",
                        json.dumps(output_data, default=str),
                        duration_ms,
                        timestamp,
                        json.dumps({}, default=str),
                    ),
                )
                db.commit()
        except Exception:
            pass

