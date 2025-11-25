from fastapi import FastAPI, Depends, HTTPException, status, Request  # Added Request import
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import jwt  # python-jwt v2.9.0
import uvicorn  # v0.32.0
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from prometheus_fastapi_instrumentator import Instrumentator  # v6.2.0
import logging
import asyncio
from slowapi import Limiter, _rate_limit_exceeded_handler  # v0.1.9
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import uuid  # For trace IDs

# Structured logging with trace IDs
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] trace_id=%(trace_id)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="Unified ML API")
security = HTTPBearer()
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Prometheus metrics
Instrumentator().instrument(app).expose(app)

JWT_SECRET = "secret"  # In prod, use env var from os.environ
ALGORITHM = "HS256"

class PredictionInput(BaseModel):
    mean: float
    var: float

def verify_jwt(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

# Shared model (load once)
class MLModel:
    def __init__(self):
        self.pipeline = Pipeline([
            ('imputer', SimpleImputer(strategy='mean')),
            ('scaler', StandardScaler()),
            ('classifier', RandomForestClassifier(random_state=42))
        ])
        # Train on dummy data (replace with real in prod)
        X_dummy = np.random.rand(100, 2)
        y_dummy = np.random.randint(0, 3, 100)
        self.pipeline.fit(X_dummy, y_dummy)

model = MLModel().pipeline

@app.post("/predict")
@limiter.limit("5/minute")
async def predict(request: Request, input: PredictionInput, user: dict = Depends(verify_jwt)):  # Added request parameter
    trace_id = str(uuid.uuid4())
    logger.info("Prediction request | input: %s", input, extra={'trace_id': trace_id})
    input_df = pd.DataFrame({'mean': [input.mean], 'var': [input.var]})
    prediction = model.predict(input_df)[0]
    return {"prediction": int(prediction), "trace_id": trace_id}

@app.post("/batch_predict")
async def batch_predict(request: Request, inputs: list[PredictionInput], user: dict = Depends(verify_jwt)):  # Added request parameter
    trace_id = str(uuid.uuid4())
    logger.info("Batch prediction | count: %d", len(inputs), extra={'trace_id': trace_id})
    df = pd.DataFrame([i.dict() for i in inputs])
    predictions = model.predict(df).tolist()
    return {"predictions": predictions, "trace_id": trace_id}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)