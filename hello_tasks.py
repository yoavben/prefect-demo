from prefect import flow, task


@task
def create_hello() -> str:
    return "hello"


@task
def create_world() -> str:
    return "world"


@flow
def hello_tasks():
    hello = create_hello()
    world = create_world()
    print(f"{hello}, {world}!")


if __name__ == '__main__':
    hello_tasks()
