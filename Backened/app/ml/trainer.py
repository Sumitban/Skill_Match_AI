import xgboost as xgb
import numpy as np
import joblib
from Backened.app.storage.mongodb import Database


class ModelTrainer:

    def __init__(self):
        self.db = Database.get_db()

    def fetch_training_data(self, job_id):
        candidates = list(
            self.db.candidates.find(
                {
                    "job_id": job_id,
                    "ranking.hr_decision": {"$ne": None}
                }
            )
        )

        if not candidates:
            return None, None

        X = []
        y = []

        for candidate in candidates:
            X.append(candidate["features"])
            y.append(candidate["ranking"]["hr_decision"])

        return np.array(X), np.array(y)

    def train(self, job_id, model_path="model.pkl"):

        X, y = self.fetch_training_data(job_id)

        if X is None:
            raise ValueError("No labeled data available for training")

        model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=4,
            learning_rate=0.1,
            use_label_encoder=False,
            eval_metric="logloss"
        )

        model.fit(X, y)

        joblib.dump(model, model_path)

        return model_path