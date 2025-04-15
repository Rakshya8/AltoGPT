class ToolAgent:
    def run(self, sensor_data: dict):
        response = {}

        # Simulate energy cost
        power_usage = sensor_data.get("power", {}).get("avg_power_watts", 0)
        hours_per_day = 24
        cost_per_kwh = 0.12  # Adjust for your region

        if power_usage:
            kwh_per_day = (power_usage * hours_per_day) / 1000
            daily_cost = kwh_per_day * cost_per_kwh
            response["daily_energy_cost_usd"] = round(daily_cost, 2)

            # Example alert
            if daily_cost > 50:
                response["alert"] = f"High energy cost detected: ${daily_cost:.2f}/day"
        else:
            response["alert"] = "Power usage data not available."

        return response