from dotenv import load_dotenv
load_dotenv()

import os, datetime as dt, zoneinfo
from flask import Flask, jsonify
from notion_client import Client


# 1) env variables
NOTION_KEY = os.getenv("NOTION_KEY")
DB_ID      = os.getenv("NOTION_DB")
PACIFIC = zoneinfo.ZoneInfo("America/Los_Angeles")   # handles PST/PDT

def build_target(ts_utc: dt.datetime) -> dt.datetime:
    """
    Return 9 AM Pacific on the same calendar day as ts_utc
    (ts_utc is the timestamp when the request arrived, in UTC).
    """
    local = ts_utc.astimezone(PACIFIC)               # convert to Pacific
    target_local = local.replace(hour=9, minute=0,
                                 second=0, microsecond=0)
    return target_local


# 2) Notion SDK client
notion = Client(auth=NOTION_KEY)

# 3) tiny helper that writes one row
def add_entry(ts_utc: dt.datetime):
    target = build_target(ts_utc)
    notion.pages.create(
        parent={"database_id": DB_ID},
        properties={
            "Date":    {"date": {"start": ts_utc.date().isoformat()}},
            "Actual Arrival Time": {"date": {"start": ts_utc.isoformat()}},
            "Goal Arrival Time":   {"date": {"start": target.isoformat()}},
        },
    )

# 4) Flask app
app = Flask(__name__)

@app.route("/log", methods=["POST"])
def log():
    add_entry(dt.datetime.utcnow())
    return jsonify(ok=True)

# 5) health-check route (handy for UptimeRobot)
@app.route("/", methods=["GET"])
def root():
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
