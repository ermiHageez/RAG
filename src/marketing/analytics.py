import csv
import io
import json
from collections import defaultdict
from datetime import datetime, timedelta
from src.marketing.sheets_tracker import SheetsTracker


class Analytics:
    def __init__(self):
        self.tracker = SheetsTracker()

    def get_campaign_summary(self, start_date: str = None, end_date: str = None) -> dict:
        leads = self.tracker.get_all_leads()

        if start_date:
            sd = datetime.fromisoformat(start_date)
            leads = [l for l in leads if datetime.fromisoformat(l["created_at"]) >= sd]
        if end_date:
            ed = datetime.fromisoformat(end_date)
            leads = [l for l in leads if datetime.fromisoformat(l["created_at"]) <= ed]

        total = len(leads)
        by_status = defaultdict(int)
        for l in leads:
            by_status[l["status"]] += 1

        sent = by_status.get("Sent", 0) + by_status.get("Opened", 0) + by_status.get("Replied", 0) + by_status.get("Meeting Booked", 0)
        opened = by_status.get("Opened", 0) + by_status.get("Replied", 0) + by_status.get("Meeting Booked", 0)
        replied = by_status.get("Replied", 0) + by_status.get("Meeting Booked", 0)
        booked = by_status.get("Meeting Booked", 0)

        return {
            "total_leads": total,
            "emails_sent": sent,
            "emails_opened": opened,
            "replies": replied,
            "meetings_booked": booked,
            "open_rate": round(opened / sent * 100, 1) if sent else 0,
            "reply_rate": round(replied / sent * 100, 1) if sent else 0,
            "conversion_rate": round(booked / sent * 100, 1) if sent else 0,
        }

    def get_product_breakdown(self) -> list[dict]:
        leads = self.tracker.get_all_leads()
        products = defaultdict(lambda: {"sent": 0, "opened": 0, "replied": 0, "booked": 0})

        for l in leads:
            p = l["product"]
            s = l["status"]
            products[p]["sent"] += 1
            if s in ("Opened", "Replied", "Meeting Booked"):
                products[p]["opened"] += 1
            if s in ("Replied", "Meeting Booked"):
                products[p]["replied"] += 1
            if s == "Meeting Booked":
                products[p]["booked"] += 1

        result = []
        for product, counts in sorted(products.items()):
            s = counts["sent"]
            result.append({
                "product": product,
                **counts,
                "open_rate": round(counts["opened"] / s * 100, 1) if s else 0,
                "reply_rate": round(counts["replied"] / s * 100, 1) if s else 0,
                "conversion_rate": round(counts["booked"] / s * 100, 1) if s else 0,
            })
        return result

    def get_timeline(self, days: int = 30) -> list[dict]:
        leads = self.tracker.get_all_leads()
        cutoff = datetime.now() - timedelta(days=days)
        daily = defaultdict(lambda: {"sent": 0, "opened": 0, "replied": 0})

        for l in leads:
            created = datetime.fromisoformat(l["created_at"])
            if created < cutoff:
                continue
            day_key = created.strftime("%Y-%m-%d")
            daily[day_key]["sent"] += 1

        result = [{"date": d, **counts} for d, counts in sorted(daily.items())]
        return result

    def export_report(self, format: str = "json") -> str:
        summary = self.get_campaign_summary()
        product_breakdown = self.get_product_breakdown()
        timeline = self.get_timeline()

        report = {
            "summary": summary,
            "product_breakdown": product_breakdown,
            "timeline": timeline,
            "generated_at": datetime.now().isoformat(),
        }

        if format == "csv":
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["Metric", "Value"])
            for key, value in summary.items():
                writer.writerow([key, value])
            writer.writerow([])
            writer.writerow(["Product", "Sent", "Opened", "Replied", "Booked", "Open Rate", "Reply Rate", "Conversion"])
            for p in product_breakdown:
                writer.writerow([p["product"], p["sent"], p["opened"], p["replied"], p["booked"], p["open_rate"], p["reply_rate"], p["conversion_rate"]])
            return output.getvalue()

        return json.dumps(report, indent=2)

    def get_top_performing_template(self) -> dict:
        products = self.get_product_breakdown()
        if not products:
            return {}
        best = max(products, key=lambda p: p["reply_rate"])
        return best
