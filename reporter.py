import time
from typing import Dict, Any, Iterable, List
import statistics
import json
from storage import JsonlWriter

def aggregate(records: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    recs = list(records)
    if not recs:
        return {"count": 0}

    count = len(recs)
    # CPU average total and per-core
    cpu_totals = [r["cpu"]["total"] for r in recs]
    cpu_per_core_list = [r["cpu"]["per_core"] for r in recs]
    # Align per-core averages
    max_cores = max(len(c) for c in cpu_per_core_list)
    per_core_avgs = []
    for i in range(max_cores):
        values = [c[i] for c in cpu_per_core_list if len(c) > i]
        per_core_avgs.append(statistics.mean(values) if values else 0)

    mem_used = [r["memory"]["used"] for r in recs]
    mem_avgs = {
        "used_avg": statistics.mean(mem_used),
    }

    # Disk and net average over time
    disks = {}
    for r in recs:
        for name, d in r.get("disk", {}).items():
            disks.setdefault(name, []).append(d.get("used", 0))
    disk_summary = {name: {"used_avg": statistics.mean(vals)} for name, vals in disks.items()}

    nets = {}
    for r in recs:
        for name, n in r.get("network", {}).items():
            nets.setdefault(name, []).append((n.get("bytes_sent", 0), n.get("bytes_recv", 0)))
    net_summary = {}
    for name, vals in nets.items():
        sent = [s for s, _ in vals]
        recv = [r for _, r in vals]
        net_summary[name] = {"bytes_sent_avg": statistics.mean(sent), "bytes_recv_avg": statistics.mean(recv)}

    return {
        "count": count,
        "cpu": {"total_avg": statistics.mean(cpu_totals), "per_core_avg": per_core_avgs},
        "memory": mem_avgs,
        "disk": disk_summary,
        "network": net_summary,
    }

def generate_summary_from_file(filepath: str, start_ts: int = None, end_ts: int = None) -> Dict[str, Any]:
    with JsonlWriter(filepath) as writer:
        recs = []
        for r in writer.read_all():
            if start_ts and r.get("timestamp", 0) < start_ts:
                continue
            if end_ts and r.get("timestamp", 0) > end_ts:
                continue
            recs.append(r)
        return aggregate(recs)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate metric summary JSON from JSONL files")
    parser.add_argument("jsonl", help="Path to JSONL file base name")
    parser.add_argument("--start", type=int, help="Start timestamp, inclusive")
    parser.add_argument("--end", type=int, help="End timestamp, inclusive")
    args = parser.parse_args()
    summary = generate_summary_from_file(args.jsonl, args.start, args.end)
    print(json.dumps(summary, indent=2))
