# Portfolio Case Study: Bias Monitoring in Signal Classification
- Problem: Imbalanced classes in signal data lead to biased predictions.
- Solution: Used class weighting in RandomForest; monitored disparate impact.
- Results: F1 improved to 0.76; impact reduced to 0.58.
- Lessons: Ethical AI requires ongoing monitoring.

# Portfolio Case Study: Unified ML API Deployment
- Problem: Fragmented ML components need consolidation for production.
- Solution: Built FastAPI service with JWT, limiting, logging, metrics; Dockerized and CI/CD to Render.
- Results: p99 <500ms; deployed at $7/mo.
- Lessons: MLOps ensures reliability.