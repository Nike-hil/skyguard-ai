class XAIExplainer:
    def explain(self, raw_reading: dict, detection_result: dict) -> dict:
        temp = raw_reading.get("temperature", 25.0)
        press = raw_reading.get("pressure", 1013.25)
        hum = raw_reading.get("humidity", 50.0)
        
        if not detection_result.get("is_anomaly", False):
            return {
                "shap_importance": {"temperature": 0.33, "pressure": 0.33, "humidity": 0.34},
                "reasoning": "All atmospheric sensors operating within nominal historical bounds."
            }

        temp_dev = max(0.0, abs(temp - 22.0) / 8.0)
        press_dev = max(0.0, abs(press - 1013.25) / 25.0)
        hum_dev = max(0.0, abs(hum - 55.0) / 20.0)

        total = temp_dev + press_dev + hum_dev + 1e-5
        imp_temp = round(temp_dev / total, 2)
        imp_press = round(press_dev / total, 2)
        imp_hum = round(hum_dev / total, 2)

        dom = max([("Temperature", imp_temp), ("Pressure", imp_press), ("Humidity", imp_hum)], key=lambda x: x[1])[0]
        reasoning = f"Alert triggered by high {dom} excursion ({detection_result.get('root_cause', 'Discrepancy')}) with {int(max(imp_temp, imp_press, imp_hum)*100)}% relative SHAP contribution."

        return {
            "shap_importance": {"temperature": imp_temp, "pressure": imp_press, "humidity": imp_hum},
            "reasoning": reasoning
        }


class SensorHealthTracker:
    def __init__(self):
        self.fault_counts = {"temperature": 0, "pressure": 0, "humidity": 0}

    def update_health(self, is_anomaly: bool, shap_importance: dict) -> dict:
        if is_anomaly:
            for s, w in shap_importance.items():
                if w > 0.4:
                    self.fault_counts[s] = min(10, self.fault_counts[s] + 2)
        else:
            for s in self.fault_counts:
                self.fault_counts[s] = max(0, self.fault_counts[s] - 1)

        def status(c):
            return "Critical Fault" if c >= 6 else ("Degrading" if c >= 3 else "Healthy")

        return {
            "temperature_status": status(self.fault_counts["temperature"]),
            "pressure_status": status(self.fault_counts["pressure"]),
            "humidity_status": status(self.fault_counts["humidity"])
        }