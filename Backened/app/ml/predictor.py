import joblib
import numpy as np
from Backened.app.storage.mongodb import Database


class ModelPredictor:

    def __init__(self, model_path="model.pkl"):
        self.model = joblib.load(model_path)
        self.db = Database.get_db()

    def predict_for_job(self, job_id):

        candidates = list(
            self.db.candidates.find({"job_id": job_id})
        )

        if not candidates:
            return []

        for candidate in candidates:
            features = np.array(candidate["features"]).reshape(1, -1)

            prob = self.model.predict_proba(features)[0][1]

            self.db.candidates.update_one(
                {"_id": candidate["_id"]},
                {
                    "$set": {
                        "ranking.prediction_score": float(prob)
                    }
                }
            )

        return True