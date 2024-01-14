from testcontainers.eventstore import EventStoreContainer
from esdbclient import EventStoreDBClient, StreamNotFound


def test_docker_run_eventstore():
    eventstore_container = EventStoreContainer()
    try:
        client = EventStoreDBClient(uri=eventstore_container.get_connection_url())
        client.read_stream("test-stream", max_count=1)
    except StreamNotFound:
        print("Server is accessible")
    except Exception as e:
        print(f"Error connecting to server: {e}")
