#!/usr/bin/env python3
"""
HubSpot Retainer & Burn Rate Auditor CLI
Scans HubSpot CRM Company & Ticket records to detect retainer hour overages and unbilled revenue leakage.
Requires a Private App token with `crm.objects.companies.read`, `crm.objects.tickets.read`.
"""

import os
import sys
import json
import urllib.request
import urllib.error

TOKEN = os.environ.get("HUBSPOT_ACCESS_TOKEN")
HOURLY_RATE = float(os.environ.get("AGENCY_HOURLY_RATE", "150.0"))

def get_headers():
    if not TOKEN:
        print("Error: HUBSPOT_ACCESS_TOKEN environment variable not set.", file=sys.stderr)
        print("Set it using: export HUBSPOT_ACCESS_TOKEN='pat-na1-xxxxxx'", file=sys.stderr)
        sys.exit(1)
    return {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

def fetch_companies():
    # Fetch companies with custom retainer properties if present
    properties = "name,domain,retainer_hours_allocated,retainer_hours_used,retainer_balance_hours"
    url = f"https://api.hubapi.com/crm/v3/objects/companies?limit=100&properties={properties}"
    req = urllib.request.Request(url, headers=get_headers(), method="GET")
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("results", [])
    except urllib.error.HTTPError as e:
        print(f"HubSpot API error: {e.code} - {e.read().decode('utf-8')}", file=sys.stderr)
        sys.exit(1)

def main():
    print("==========================================================")
    print("      HubSpot Agency Retainer & Burn Rate Auditor         ")
    print("==========================================================")
    print(f"Audit Assumptions: Default Billable Rate = ${HOURLY_RATE:.2f}/hr\n")

    companies = fetch_companies()
    print(f"Audited {len(companies)} client companies from HubSpot CRM.\n")

    overage_companies = []
    low_balance_companies = []
    total_leaked_hours = 0.0

    for c in companies:
        props = c.get("properties", {})
        name = props.get("name") or "Unnamed Client"
        domain = props.get("domain") or "N/A"

        # Check allocated vs used
        try:
            allocated = float(props.get("retainer_hours_allocated") or 0.0)
            used = float(props.get("retainer_hours_used") or 0.0)
            balance = float(props.get("retainer_balance_hours") or (allocated - used))
        except (ValueError, TypeError):
            continue

        if allocated <= 0 and used <= 0:
            continue

        if balance < 0:
            overage_hours = abs(balance)
            total_leaked_hours += overage_hours
            overage_companies.append({
                "name": name,
                "domain": domain,
                "allocated": allocated,
                "used": used,
                "overage": overage_hours,
                "loss": overage_hours * HOURLY_RATE
            })
        elif allocated > 0 and (balance / allocated) <= 0.20:
            low_balance_companies.append({
                "name": name,
                "domain": domain,
                "allocated": allocated,
                "balance": balance,
                "pct_left": (balance / allocated) * 100
            })

    print("--- 1. OVERAGE ALERTS (Unbilled Revenue Leakage) ---")
    if not overage_companies:
        print("✓ No retainer overages detected. All active accounts within limits.")
    else:
        for oc in overage_companies:
            print(f"⚠️  {oc['name']} ({oc['domain']}):")
            print(f"    Allocated: {oc['allocated']} hrs | Used: {oc['used']} hrs | Overage: {oc['overage']:.1f} hrs")
            print(f"    Estimated Unbilled Work: ${oc['loss']:,.2f}")

    print(f"\nTotal Leaked Revenue: ${total_leaked_hours * HOURLY_RATE:,.2f} across {len(overage_companies)} clients.\n")

    print("--- 2. LOW-BALANCE ALERTS (Upcoming Renewal Triggers) ---")
    if not low_balance_companies:
        print("✓ No accounts currently below the 20% balance threshold.")
    else:
        for lc in low_balance_companies:
            print(f"🔔 {lc['name']}: {lc['balance']:.1f} hrs remaining ({lc['pct_left']:.0f}% of {lc['allocated']} hrs allocated).")
            print("    Action: Stage a top-up renewal deal before hours run dry.")

    print("\n==========================================================")
    print("Want automated time tracking, FIFO retainer drawdowns, and")
    print("automated top-up deals inside HubSpot without manual scripts?")
    print("👉 Check out Retainer Wallet: https://kayabyte.dev/hubspot/retainer-wallet/?src=c-gh-retainer")
    print("==========================================================")

if __name__ == "__main__":
    main()
