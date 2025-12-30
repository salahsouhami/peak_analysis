from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
from datetime import datetime, timedelta

app = FastAPI()

class Item(BaseModel):
    timestamp: float
    power_kw: float

@app.post("/analyze")
def analyze(items: list[Item]):
    df = pd.DataFrame([i.dict() for i in items])

    excel_epoch = datetime(1899, 12, 30)
    df["timestamp"] = df["timestamp"].apply(
        lambda x: excel_epoch + timedelta(days=float(x))
    )

    peak = df.loc[df["power_kw"].idxmax()]

    return {
        "peak_kw": float(peak["power_kw"]),
        "peak_time": peak["timestamp"].strftime("%Y-%m-%d %H:%M")
    }
