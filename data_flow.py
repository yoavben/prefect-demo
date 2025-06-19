from prefect import flow, task
import time
import random
from typing import List, Dict, Any
import asyncio


@task(retries=2, retry_delay_seconds=1)
def fetch_data(source_id: int) -> Dict[str, Any]:
    """Simulate fetching data from an external source"""
    print(f"Fetching data from source {source_id}...")
    # Simulate network delay
    time.sleep(random.uniform(0.5, 2))
    
    # Randomly fail sometimes to demonstrate retries
    if random.random() < 0.2:
        raise Exception(f"Failed to fetch data from source {source_id}")
    
    return {
        "source_id": source_id,
        "data": random.randint(100, 1000),
        "timestamp": time.time()
    }


@task
def process_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Process the fetched data"""
    print(f"Processing data from source {data['source_id']}...")
    # Simulate processing time
    time.sleep(random.uniform(0.3, 1))
    
    # Add processed fields
    data["processed"] = True
    data["processed_value"] = data["data"] * 2
    return data


@task
def aggregate_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Aggregate all the processed results"""
    print(f"Aggregating {len(results)} results...")
    
    total = sum(result["processed_value"] for result in results)
    average = total / len(results)
    
    return {
        "total": total,
        "average": average,
        "count": len(results),
        "sources": [r["source_id"] for r in results]
    }


@task
def save_results(aggregated_data: Dict[str, Any]) -> str:
    """Save the aggregated results"""
    print(f"Saving aggregated results: {aggregated_data}...")
    # Simulate database write
    time.sleep(0.5)
    return f"Results saved successfully: {len(aggregated_data['sources'])} sources processed"


@flow(name="parallel-data-processing")
def parallel_data_flow(num_sources: int = 5):
    """
    Demonstrates different patterns of using submit() and futures in Prefect
    """
    print(f"Starting parallel data processing for {num_sources} sources")
    
    # Pattern 1: Submitting all tasks at once and collecting futures
    fetch_futures = []
    for i in range(num_sources):
        future = fetch_data.submit(source_id=i)
        fetch_futures.append(future)
    
    # Pattern 2: Dependent tasks with wait-for-all pattern
    process_futures = []
    for future in fetch_futures:
        # This won't execute until the fetch task completes
        try:
            data = future.result()  # This blocks until the fetch task is done
            process_future = process_data.submit(data=data)
            process_futures.append(process_future)
        except Exception as e:
            print(f"Skipping failed fetch: {e}")
    
    # Pattern 3: Collecting all results before proceeding
    processed_results = []
    for future in process_futures:
        processed_results.append(future.result())
    
    # Pattern 4: Submitting a task that depends on all previous tasks
    aggregated_future = aggregate_results.submit(results=processed_results)
    
    # Pattern 5: Final dependent task with immediate result
    final_result = save_results(aggregated_data=aggregated_future.result())
    
    print(f"Flow completed: {final_result}")
    return final_result


@flow(name="advanced-parallel-data-flow")
def advanced_parallel_flow(num_sources: int = 5):
    """
    An advanced example showing conditional execution based on futures
    """
    # Submit all fetch operations in parallel
    fetch_futures = [fetch_data.submit(source_id=i) for i in range(num_sources)]
    
    # Create dictionary to track which futures are completed
    completed_fetches = {}
    failed_fetches = []
    
    # Check futures as they complete
    for i, future in enumerate(fetch_futures):
        try:
            result = future.result()
            completed_fetches[i] = result
        except Exception as e:
            failed_fetches.append((i, str(e)))
    
    # Log failures if any
    if failed_fetches:
        print(f"Failed to fetch from {len(failed_fetches)} sources: {failed_fetches}")
    
    # Only process if we have at least 3 successful fetches
    if len(completed_fetches) >= 3:
        # Process all successful fetches in parallel
        process_futures = [process_data.submit(data=data) for data in completed_fetches.values()]
        
        # Wait for all processing to complete and collect results
        processed_results = [future.result() for future in process_futures]
        
        # Aggregate and save
        aggregated = aggregate_results.submit(results=processed_results).result()
        return save_results(aggregated_data=aggregated)
    else:
        print(f"Not enough data sources available. Only {len(completed_fetches)} succeeded, needed at least 3.")
        return f"Flow failed: insufficient data sources ({len(completed_fetches)}/{num_sources})"


if __name__ == "__main__":
    print("\n--- Running basic parallel flow ---\n")
    parallel_data_flow(num_sources=5)
    
    print("\n--- Running advanced parallel flow ---\n")
    advanced_parallel_flow(num_sources=6)