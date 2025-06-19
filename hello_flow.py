from prefect import flow
import myflow

@flow
def hello_flow():
    print("Hello, world!")


if __name__ == '__main__':
    hello_flow()
