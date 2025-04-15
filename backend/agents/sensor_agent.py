import stat
import pandas as pd
# import dateparser

from utils.data_loader import load_iaq, load_power, load_presence

# def extract_datetime_from_question(date_str: str):
#     dt = dateparser.parse(date_str, settings={"PREFER_DATES_FROM": "past"})
#     return pd.to_datetime(dt)

class SensorAgent:
    def __init__(self, room: str, operation: str, datetime: str):
        self.room = room
        self.operation = operation
        self.datetime = datetime

    def get_iaq_summary(self):
        df = load_iaq(self.room)
        df['datetime'] = pd.to_datetime(df['datetime'])

        if self.operation == "average":
            co2 = round(df["co2"].mean(), 2)
            temp = round(df["temperature"].mean(), 2)
            humidity = round(df["humidity"].mean(), 2)
            status = "Success"

        elif self.operation == "sum":
            co2 = round(df["co2"].sum(), 2)
            temp = round(df["temperature"].sum(), 2)
            humidity = round(df["humidity"].sum(), 2)
            status = "Success"

        elif self.operation == "time_specific":
            parsed_time = pd.to_datetime(self.datetime)
            nearest_idx = (df['datetime'] - parsed_time).abs().idxmin()
            closest_time = df.loc[nearest_idx, "datetime"]
            time_diff = abs(closest_time - parsed_time)

            # Set a threshold, e.g., 1 hour
            threshold = pd.Timedelta(hours=1)

            if time_diff > threshold:
                print(f"No close data available for the requested time {parsed_time}. Closest is {closest_time}.")
                status = "Failure"
            else:
                co2 = round(df["co2"][nearest_idx], 2)
                temp = round(df["temperature"][nearest_idx], 2)
                humidity = round(df["humidity"][nearest_idx], 2)
                status = "Success"

        elif self.operation == "latest":
            latest = df.iloc[-1]
            co2 = latest["co2"]
            temp = latest["temperature"]
            humidity = latest["humidity"]
            status = "Success"

        else:
            status = "Failure"

        if status == "Failure":
            return {
                "status": status,
                "message": f"Invalid operation '{self.operation}' or no data available for the requested time."
            }
        else:
            # Check for IAQ alerts
            alerts = []
            if co2 > 1000:
                alerts.append(f"CO2 is high at {co2} ppm (ASHRAE limit: 1000 ppm).")
            if temp > 28:
                alerts.append(f"Temperature is warm at {temp}°C.")
            if humidity > 60:
                alerts.append(f"Humidity is high at {humidity}%.")

            return {
                "co2": co2,
                "temperature": temp,
                "humidity": humidity,
                "iaq_alerts": alerts,
                "status": status
            }

    def get_power_summary(self):
        df = load_power()

        power_columns = [
            "power_kw_power_meter_1",
            "power_kw_power_meter_2",
            "power_kw_power_meter_3",
            "power_kw_power_meter_4",
            "power_kw_power_meter_5",
            "power_kw_power_meter_6"
        ]

        df["total_kw"] = df[power_columns].sum(axis=1)
        avg_kw = df["total_kw"].tail(10).mean()
        avg_watts = avg_kw * 1000

        return {"avg_power_watts": avg_watts}

    def get_presence_summary(self):
        df = load_presence(self.room)
        last = df.iloc[-1]
        return {"occupied": bool(last["presence_state"])}


    def run(self):
        iaq = self.get_iaq_summary()
        power = self.get_power_summary()
        presence = self.get_presence_summary()

        return {
            "iaq": iaq,
            "power": power,
            "presence": presence,
            "status": iaq["status"]
        }
