from prefect import flow, task
from prefect.futures import PrefectFuture


@task
def create_hello() -> str:
    return "hello"


@task
def create_world() -> str:
    return "world"


@flow
def parallel_tasks():
    hello_future: PrefectFuture = create_hello.submit()
    world_future: PrefectFuture = create_world.submit()
    print(f"{hello_future.result()}, {world_future.result()}!")


if __name__ == '__main__':
    parallel_tasks()
