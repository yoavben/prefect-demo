from prefect import flow, task


@task
def create_hello() -> str:
    return "hello"


@task
def create_world() -> str:
    return "world"


@flow
def parallel_tasks():
    hello_future = create_hello.submit()
    world_future = create_world.submit()
    print(f"{hello_future.result()}, {world_future.result()}!")


if __name__ == '__main__':
    parallel_tasks()