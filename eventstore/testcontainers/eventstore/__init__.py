#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
from esdbclient import EventStoreDBClient
import os
from testcontainers.core.container import DockerContainer
from testcontainers.core.utils import raise_for_deprecated_parameter
from testcontainers.core.waiting_utils import wait_container_is_ready, wait_for_logs
from typing import Optional


class EventStoreContainer(DockerContainer):
    """
    EventStore container.

    Example:

        The example spins up an EventStore cluster and connects to it using the
        :code:`esdbclient` client.


        .. doctest::

            >>> from testcontainers.eventstore import EventStoreContainer
            >>> from esdbclient import EventStoreDBClient, StreamNotFound

            >>> with EventStoreContainer() as eventstore
            >>>     try:
            ...         client = eventstore.get_connection_client()
            ...         client.read_stream("test-stream", max_count=1)
            ...     except StreamNotFound:
            ...         print("Server is accessible")
            ...     except Exception as e:
            ...         print(f"Error connecting to server: {e}")
    """

    def __init__(
        self,
        image: str = "eventstore/eventstore:latest",
        http_port: int = 2113,
        tcp_port: int = 1113,
        cluster_size: int = 1,
        run_projections: str = "all",
        start_standard_projections: bool = True,
        insecure: bool = True,
        enable_atom_pub_over_http: bool = True,
        **kwargs,
    ) -> None:
        super(EventStoreContainer, self).__init__(image=image, remove=False, **kwargs)
        self._command = "--insecure"
        self.http_port = http_port or os.environ.get("EVENTSTORE_HTTP_PORT", None)
        self.ext_tcp_port = tcp_port or os.environ.get("EVENTSTORE_EXT_TCP_PORT", None)
        self.cluster_size = cluster_size or os.environ.get("EVENTSTORE_CLUSTER_SIZE", 1)
        self.run_projections = run_projections or os.environ.get(
            "EVENTSTORE_RUN_PROJECTIONS", "all"
        )
        self.start_standard_projections = start_standard_projections or os.environ.get(
            "EVENTSTORE_START_STANDARD_PROJECTIONS", True
        )
        self.insecure = insecure or os.environ.get("EVENTSTORE_INSECURE", True)
        if not self.insecure:
            raise Exception(
                "Accessing secure EventStore clusters is currently unsupported"
            )
        self.enable_atom_pub_over_http = enable_atom_pub_over_http or os.environ.get(
            "EVENTSTORE_ENABLE_ATOM_PUB_OVER_HTTP", True
        )

        if self.http_port:
            self.with_exposed_ports(self.http_port)
        if self.ext_tcp_port:
            self.with_exposed_ports(self.ext_tcp_port)

    def start(self) -> "EventStoreContainer":
        self._configure()
        super().start()
        delay = wait_for_logs(
            self, '.*"InaugurationManager" in state \\(Leader, Idle\\).*'
        )
        self._connect()
        return self

    def _configure(self) -> None:
        self.with_env("EVENTSTORE_CLUSTER_SIZE", self.cluster_size)
        self.with_env("EVENTSTORE_RUN_PROJECTIONS", self.run_projections)
        self.with_env(
            "EVENTSTORE_START_STANDARD_PROJECTIONS", self.start_standard_projections
        )
        self.with_env("EVENTSTORE_EXT_TCP_PORT", self.ext_tcp_port)
        self.with_env("EVENTSTORE_HTTP_PORT", self.http_port)
        self.with_env("EVENTSTORE_INSECURE", self.insecure)
        self.with_env(
            "EVENTSTORE_ENABLE_ATOM_PUB_OVER_HTTP", self.enable_atom_pub_over_http
        )

    def get_connection_url(self, host=None) -> str:
        if self.insecure:
            port = self.get_exposed_port(self.http_port)
            return f"esdb://0.0.0.0:{port}?Tls=false"
        else:
            raise Exception(
                "Accessing secure EventStore clusters is currently unsupported"
            )

    @wait_container_is_ready()
    def _connect(self) -> EventStoreDBClient:
        return EventStoreDBClient(uri=self.get_connection_url())

    def get_connection_client(self) -> EventStoreDBClient:
        return self._connect()
