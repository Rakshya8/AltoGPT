class AnswerAgent:
    def __init__(self):
        pass

    def generate(self, sensor_data: dict, guidelines: dict) -> str:
        iaq = sensor_data["iaq"]
        power = sensor_data["power"]
        presence = sensor_data["presence"]

        room_status = []

        # IAQ alerts
        for alert in iaq["iaq_alerts"]:
            room_status.append(alert)
        
        if not iaq["iaq_alerts"]:
            room_status.append("Indoor air quality is within acceptable limits.")

        # Power summary
        room_status.append(f"Recent average power usage: {power['avg_power_watts']:.2f} W.")

        # Presence
        occupancy = "occupied" if presence["occupied"] else "unoccupied"
        room_status.append(f"The room is currently {occupancy}.")

        # Guidelines
        guideline_texts = [f"{k.upper()}: {v}" for k, v in guidelines.items()]
        guideline_block = "\n".join(guideline_texts)
        status_block = "- " + "\n- ".join(room_status)

        return f"""Room Analysis:
{status_block}

Guidelines Reference:
{guideline_block}
"""
