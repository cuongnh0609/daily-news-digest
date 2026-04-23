#!/usr/bin/env python3
"""Analyze stream-json log from `claude --output-format stream-json`.
Reports bottlenecks: per-tool timings, parallelism, generation vs. tool time.

Usage:  ./scripts/analyze_log.py logs/stream_YYYY-MM-DD_HHMMSS.jsonl
"""

import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path


def parse_ts(s):
    if not s:
        return None
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def iter_events(path):
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def analyze(path):
    events = list(iter_events(path))
    if not events:
        print(f"No events in {path}")
        return

    # Extract timings — events either have a `timestamp` at top level or nested.
    # Stream-json from claude includes `type` field; tool_use blocks appear in
    # assistant messages, tool_result blocks in user messages.
    tool_calls = {}  # tool_use_id -> {name, input, started, ended}
    turns = []  # list of (turn_idx, started_at, ended_at, tool_uses_in_turn)
    assistant_turn_start = None
    current_turn_tools = []
    total_start = None
    total_end = None
    result_event = None

    for ev in events:
        ts = ev.get("timestamp")  # may be absent for some event types
        if total_start is None and ts:
            total_start = ts
        if ts:
            total_end = ts

        t = ev.get("type")

        if t == "assistant":
            msg = ev.get("message", {})
            content = msg.get("content", [])
            if not isinstance(content, list):
                continue
            for block in content:
                if not isinstance(block, dict):
                    continue
                if block.get("type") == "tool_use":
                    tid = block.get("id")
                    tool_calls[tid] = {
                        "name": block.get("name", "unknown"),
                        "input": block.get("input", {}),
                        "started_msg_ts": ts,
                        "ended_msg_ts": None,
                    }
                    current_turn_tools.append(tid)
        elif t == "user":
            msg = ev.get("message", {})
            content = msg.get("content", [])
            if not isinstance(content, list):
                continue
            for block in content:
                if not isinstance(block, dict):
                    continue
                if block.get("type") == "tool_result":
                    tid = block.get("tool_use_id")
                    if tid in tool_calls:
                        tool_calls[tid]["ended_msg_ts"] = ts
                        tool_calls[tid]["is_error"] = block.get("is_error", False)
        elif t == "result":
            result_event = ev

    # Group by tool name
    per_tool = defaultdict(list)
    for tid, info in tool_calls.items():
        per_tool[info["name"]].append(info)

    # Header
    print(f"=== Analysis of {Path(path).name} ===")
    if total_start and total_end:
        print(f"First event ts: {total_start}")
        print(f"Last event ts : {total_end}")
    print(f"Total events  : {len(events)}")
    print(f"Total tool calls: {len(tool_calls)}")
    print()

    # Per-call latency (tool_use ts → tool_result ts)
    for info in tool_calls.values():
        s = parse_ts(info.get("started_msg_ts"))
        e = parse_ts(info.get("ended_msg_ts"))
        info["latency_s"] = (e - s).total_seconds() if s and e else None

    # Per-tool summary with timing
    print(f"{'Tool':<14} {'Count':>5} {'Err':>4} {'Total_s':>8} {'Avg_s':>7} {'Max_s':>7} {'P50':>6} {'P90':>6}")
    print("-" * 66)
    grand_tool_s = 0.0
    for name in sorted(per_tool):
        calls = per_tool[name]
        errs = sum(1 for c in calls if c.get("is_error"))
        lats = sorted(c["latency_s"] for c in calls if c["latency_s"] is not None)
        if lats:
            total = sum(lats)
            avg = total / len(lats)
            mx = lats[-1]
            p50 = lats[len(lats) // 2]
            p90 = lats[min(len(lats) - 1, int(len(lats) * 0.9))]
            grand_tool_s += total
            print(f"{name:<14} {len(calls):>5} {errs:>4} {total:>8.1f} {avg:>7.1f} {mx:>7.1f} {p50:>6.1f} {p90:>6.1f}")
        else:
            print(f"{name:<14} {len(calls):>5} {errs:>4} {'--':>8} {'--':>7} {'--':>7} {'--':>6} {'--':>6}")
    print(f"{'TOTAL':<14} {len(tool_calls):>5} {'':>4} {grand_tool_s:>8.1f}")
    print()

    # Top 5 slowest calls
    slow = sorted(tool_calls.values(), key=lambda c: c.get("latency_s") or 0, reverse=True)[:5]
    print("Top 5 slowest tool calls:")
    for c in slow:
        if c.get("latency_s") is None:
            continue
        inp = c["input"]
        detail = inp.get("url") or inp.get("query") or inp.get("command") or inp.get("file_path") or str(inp)[:60]
        if len(str(detail)) > 70:
            detail = str(detail)[:67] + "..."
        err = " [ERR]" if c.get("is_error") else ""
        print(f"  {c['latency_s']:>6.1f}s  {c['name']:<12}{err:<6} {detail}")
    print()

    # Parallelism: group tool_use by message timestamp → how many tool_use per assistant turn
    per_turn = defaultdict(int)
    for tid, info in tool_calls.items():
        per_turn[info["started_msg_ts"]] += 1

    if per_turn:
        parallel_counts = defaultdict(int)
        for _ts, n in per_turn.items():
            parallel_counts[n] += 1
        print("Tool-calls-per-turn distribution (how parallel is Claude being?):")
        for n in sorted(parallel_counts):
            label = "sequential (1 call)" if n == 1 else f"{n} calls parallel"
            print(f"  {label:<25} → {parallel_counts[n]} turns")
        print()

    # Token / cost summary from result event
    if result_event:
        usage = result_event.get("usage", {})
        duration_ms = result_event.get("duration_ms")
        duration_api_ms = result_event.get("duration_api_ms")
        num_turns = result_event.get("num_turns")
        print("From final `result` event:")
        if duration_ms is not None:
            print(f"  duration_ms     (wall)  : {duration_ms:>8} ms  ({duration_ms/1000:.1f}s)")
        if duration_api_ms is not None:
            print(f"  duration_api_ms (API)   : {duration_api_ms:>8} ms  ({duration_api_ms/1000:.1f}s)")
            if duration_ms:
                tool_pct = (1 - duration_api_ms / duration_ms) * 100
                print(f"  → non-API time (tools+thinking): {tool_pct:.1f}% of wall time")
        if num_turns is not None:
            print(f"  num_turns               : {num_turns}")
        if usage:
            print(f"  input_tokens            : {usage.get('input_tokens', '?')}")
            print(f"  output_tokens           : {usage.get('output_tokens', '?')}")
            print(f"  cache_read_tokens       : {usage.get('cache_read_input_tokens', '?')}")
            print(f"  cache_creation_tokens   : {usage.get('cache_creation_input_tokens', '?')}")
        print()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <stream-log.jsonl>", file=sys.stderr)
        sys.exit(2)
    analyze(sys.argv[1])
