from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from app.api.dependencies import get_analytics_repository
from app.core.ws_manager import analytics_ws_manager
from app.repositories.analytics_repository import AnalyticsRepository

router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws/analytics")
async def analytics_updates(
    websocket: WebSocket,
    repository: AnalyticsRepository = Depends(get_analytics_repository),
):
    """
    Pushes a message whenever the analytics materialized views are
    refreshed (see AnalyticsRepository.refresh_views + app/worker.py),
    so a dashboard can show "last updated" live instead of polling.
    """
    await analytics_ws_manager.connect(websocket)

    last_refreshed_at = await repository.get_last_refreshed_at()
    await websocket.send_json(
        {
            "event": "connected",
            "refreshed_at": (
                last_refreshed_at.isoformat() if last_refreshed_at else None
            ),
        }
    )

    try:
        while True:
            # This endpoint is push-only; block here until the client
            # disconnects (any inbound message is simply ignored).
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        await analytics_ws_manager.disconnect(websocket)
