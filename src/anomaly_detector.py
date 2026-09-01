class AnomalyDetector:
    def __init__(self, model_path=None):
        self.history = []

    def predict_reading(self, reading: dict) -> dict:
        temp = reading.get("temperature", 0.0)
        press = reading.get("pressure", 1013.25)
        hum = reading.get("humidity", 50.0)

        is_anomaly = False
        anomaly_score = 0.08
        root_cause = "Normal Operation"

        if temp < -40.0 or temp > 55.0 or press < 800.0 or press > 1100.0 or hum < 0.0 or hum > 100.0:
            is_anomaly = True
            anomaly_score = 0.98
            root_cause = "Hardware / Out-of-Bounds Error"
        elif temp > 42.0 or (len(self.history) > 0 and abs(temp - self.history[-1]["temperature"]) > 8.0):
            is_anomaly = True
            anomaly_score = 0.92
            root_cause = "Instantaneous Thermal Spike"
        elif len(self.history) >= 4 and len(set([h["temperature"] for h in self.history[-4:]] + [temp])) == 1:
            is_anomaly = True
            anomaly_score = 0.86
            root_cause = "Frozen Sensor Output"
        elif temp > 35.0 and hum > 90.0 and press < 960.0:
            is_anomaly = True
            anomaly_score = 0.78
            root_cause = "Multivariate Atmospheric Inconsistency"

        self.history.append(reading)
        if len(self.history) > 30:
            self.history.pop(0)

        return {
            "is_anomaly": is_anomaly,
            "anomaly_score": round(float(anomaly_score), 2),
            "root_cause": root_cause
        }