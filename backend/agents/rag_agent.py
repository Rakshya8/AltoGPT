class RAGAgent:
    def __init__(self):
        # Mock "knowledge base"
        self.guidelines = {
            "co2": "ASHRAE recommends indoor CO2 stay below 1000 ppm.",
            "temperature": "Recommended indoor temperature is 21-24°C for comfort.",
            "humidity": "Humidity should be between 30-60% for healthy indoor air.",
            "power": "Reducing energy use in unoccupied rooms is advised.",
            "presence": "Presence data can be used to optimize HVAC and lighting.",
        }

    def retrieve(self, topic: str) -> str:
        return self.guidelines.get(topic, "No standard available.")
