import asyncio
import json
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from app.core.deps import get_current_active_user
from app.models.user import User

router = APIRouter()

# In-memory event bus for SSE notifications
# Stores pending events per user_id
_notification_queues: dict[str, list[asyncio.Queue]] = {}


async def emit_cobro_notification(
    usuario_nombre: str,
    usuario_email: str,
    monto: float,
    inquilino_nombre: str,
    inmueble_direccion: str,
):
    """Broadcast a cobro notification to all connected admin clients."""
    event_data = json.dumps({
        "type": "cobro_realizado",
        "usuario_nombre": usuario_nombre,
        "usuario_email": usuario_email,
        "monto": monto,
        "inquilino_nombre": inquilino_nombre,
        "inmueble_direccion": inmueble_direccion,
    })
    dead_queues = []
    for user_id, queues in _notification_queues.items():
        for q in queues:
            try:
                q.put_nowait(event_data)
            except asyncio.QueueFull:
                dead_queues.append((user_id, q))
    # Clean up full queues
    for uid, q in dead_queues:
        if uid in _notification_queues and q in _notification_queues[uid]:
            _notification_queues[uid].remove(q)


@router.get("/stream")
async def notification_stream(
    current_user: User = Depends(get_current_active_user),
):
    """SSE endpoint. Only admin users receive cobro notifications."""
    queue: asyncio.Queue = asyncio.Queue(maxsize=50)
    user_id = current_user.id

    if user_id not in _notification_queues:
        _notification_queues[user_id] = []
    _notification_queues[user_id].append(queue)

    async def event_generator():
        try:
            # Send initial connection confirmation
            yield f"data: {json.dumps({'type': 'connected'})}\n\n"
            while True:
                try:
                    data = await asyncio.wait_for(queue.get(), timeout=30)
                    yield f"data: {data}\n\n"
                except asyncio.TimeoutError:
                    # Keep-alive ping
                    yield f": keepalive\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            if user_id in _notification_queues and queue in _notification_queues[user_id]:
                _notification_queues[user_id].remove(queue)
                if not _notification_queues[user_id]:
                    del _notification_queues[user_id]

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
