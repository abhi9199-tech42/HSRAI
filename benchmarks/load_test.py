#!/usr/bin/env python3
"""HSRAI Load/Stress Testing Script.

Usage:
    python benchmarks/load_test.py [--url http://localhost:8000] [--concurrent 10] [--requests 100]

Measures throughput, latency percentiles, and error rates.
"""

import argparse
import asyncio
import time
import statistics
import sys
from typing import List


async def make_request(
    session, url: str, text: str, api_key: str, results: list, errors: list
):
    start = time.monotonic()
    try:
        import aiohttp
        async with session.post(
            f"{url}/process",
            json={"text": text},
            headers={"X-API-Key": api_key, "Content-Type": "application/json"},
            timeout=aiohttp.ClientTimeout(total=30),
        ) as resp:
            elapsed = (time.monotonic() - start) * 1000
            if resp.status == 200:
                results.append(elapsed)
            else:
                errors.append(resp.status)
    except Exception as e:
        elapsed = (time.monotonic() - start) * 1000
        errors.append(str(e))
        results.append(elapsed)


async def run_load_test(url: str, concurrent: int, total_requests: int, api_key: str):
    try:
        import aiohttp
    except ImportError:
        print("aiohttp required: pip install aiohttp")
        sys.exit(1)

    texts = [
        "Analyze transaction TX001 for fraud risk",
        "What is the diagnosis for patient with fever and cough?",
        "Process this query about account security",
        "Review compliance for regulatory filing",
        "Evaluate risk assessment for loan application",
    ]

    print(f"HSRAI Load Test")
    print(f"  URL: {url}")
    print(f"  Concurrent: {concurrent}")
    print(f"  Total requests: {total_requests}")
    print(f"  API Key: {'*' * len(api_key)}")
    print()

    results: List[float] = []
    errors: List[int] = []
    semaphore = asyncio.Semaphore(concurrent)

    async def bounded_request(session, text, idx):
        async with semaphore:
            await make_request(session, url, text, api_key, results, errors)

    start_time = time.monotonic()
    async with aiohttp.ClientSession() as session:
        tasks = [
            bounded_request(session, texts[i % len(texts)], i)
            for i in range(total_requests)
        ]
        await asyncio.gather(*tasks)
    total_time = time.monotonic() - start_time

    if not results:
        print("No successful requests")
        return

    print(f"Results:")
    print(f"  Total time: {total_time:.2f}s")
    print(f"  Throughput: {len(results) / total_time:.1f} req/s")
    print(f"  Successful: {len(results)}")
    print(f"  Errors: {len(errors)}")
    if errors:
        from collections import Counter
        error_counts = Counter(errors)
        for code, count in error_counts.most_common():
            print(f"    {code}: {count}")

    sorted_results = sorted(results)
    print(f"  Latency (ms):")
    print(f"    min:    {sorted_results[0]:.1f}")
    print(f"    median: {sorted_results[len(sorted_results) // 2]:.1f}")
    print(f"    p95:    {sorted_results[int(len(sorted_results) * 0.95)]:.1f}")
    print(f"    p99:    {sorted_results[int(len(sorted_results) * 0.99)]:.1f}")
    print(f"    max:    {sorted_results[-1]:.1f}")
    print(f"    mean:   {statistics.mean(results):.1f}")
    print(f"    stdev:  {statistics.stdev(results):.1f}" if len(results) > 1 else "")


def main():
    parser = argparse.ArgumentParser(description="HSRAI Load Test")
    parser.add_argument("--url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--concurrent", type=int, default=10, help="Concurrent requests")
    parser.add_argument("--requests", type=int, default=100, help="Total requests")
    parser.add_argument("--api-key", default="changeme", help="API key")
    args = parser.parse_args()
    asyncio.run(run_load_test(args.url, args.concurrent, args.requests, args.api_key))


if __name__ == "__main__":
    main()
