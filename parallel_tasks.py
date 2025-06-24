import time

from prefect import flow, task, get_run_logger
from prefect.futures import PrefectFuture


@task
def create_hello() -> str:
    time.sleep(2)
    return "hello"


@task
def create_world() -> str:
    time.sleep(2)
    return "world"


@flow
def parallel_tasks():
    start_time = time.time()
    hello_future: PrefectFuture = create_hello.submit()
    world_future: PrefectFuture = create_world.submit()
    end_time = time.time()
    print(f"{hello_future.result()}, {world_future.result()}, duration: {end_time - start_time}!")
    get_run_logger().info(
        f"flow finished. duration:{end_time-start_time:.2f}s"
    )



if __name__ == '__main__':
    parallel_tasks()
