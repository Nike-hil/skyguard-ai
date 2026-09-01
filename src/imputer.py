class DataImputer:
    def init(self):
        self.last_valid = {"temperature": 22.5, "pressure": 1013.2, "humidity": 55.0}

    def impute(self, raw_reading: dict, is_anomaly: bool, shap_importance: dict) -> dict:
        corrected = dict(raw_reading)
        if not is_anomaly:
            self.last_valid = dict(raw_reading)
            return {
                "corrected_temperature": round(raw_reading["temperature"], 2),
                "corrected_pressure": round(raw_reading["pressure"], 2),
                "corrected_humidity": round(raw_reading["humidity"], 2)
            }

        if shap_importance.get("temperature", 0) > 0.4:
            corrected["temperature"] = self.last_valid["temperature"] + 0.05
        if shap_importance.get("pressure", 0) > 0.4:
            corrected["pressure"] = self.last_valid["pressure"]
        if shap_importance.get("humidity", 0) > 0.4:
            corrected["humidity"] = self.last_valid["humidity"]

        return {
            "corrected_temperature": round(corrected["temperature"], 2),
            "corrected_pressure": round(corrected["pressure"], 2),
            "corrected_humidity": round(corrected["humidity"], 2)
        }