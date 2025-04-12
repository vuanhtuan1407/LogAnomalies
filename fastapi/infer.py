import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd

# Load the trained model
with open('../data/BGL/random_forest_log.pkl', 'rb') as f:
    model, _ = joblib.load(f)

app = FastAPI()


# Define a schema for input data
class LogData(BaseModel):
    rack: int
    midplane: int
    node_type: int
    node_no: int
    control_IO: int
    jid: int
    uid: int
    type: int
    eventId: int
    channel_A: int
    channel_C: int
    channel_D: int
    channel_E: int
    channel_S: int
    component_APP: int
    component_BGLMASTER: int
    component_CMCS: int
    component_DISCOVERY: int
    component_HARDWARE: int
    component_KERNEL: int
    component_LINKCARD: int
    component_MMCS: int
    component_MONITOR: int
    component_SERV_NET: int
    level_ERROR: int
    level_FAILURE: int
    level_FATAL: int
    level_INFO: int
    level_SEVERE: int
    level_WARNING: int


# Define the prediction endpoint
@app.post("/predict/")
def predict_anomaly(log_data: LogData):
    data = pd.DataFrame([log_data.model_dump(mode='json')])
    prediction = model.predict(data)[0]
    result = "Alert" if prediction == 1 else "Non-alert"
    return {"Label": result}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
