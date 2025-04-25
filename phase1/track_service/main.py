from fastapi import FastAPI
from Projects.phase1.track_service.schemas import AppEvent
from Projects.phase1.track_service.producer import produce_event

app = FastAPI()

@app.post("/track")
def track(event: AppEvent):
    produce_event(event.model_dump())
    return {"status": "ok", "event": event}



