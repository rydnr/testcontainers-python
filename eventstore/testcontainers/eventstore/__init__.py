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
import os
from typing import Optional
from testcontainers.core.container import DockerContainer
from testcontainers.core.utils import raise_for_deprecated_parameter


class EventStoreContainer(DockerContainer):
    """
    EventStore container.

    Example:

        The example spins up an EventStore cluster and connects to it using the
        :code:`esdbclient` client.


        .. doctest::

            >>> from testcontainers.eventstore import EventStoreContainer
            >>> from esdbclient import AsyncioEventStoreDBClient, StreamNotFound

            >>> eventstore_container = EventStoreContainer("eventstore:v23.10.0")
            >>> try:
            ...     client = await AsyncioEventStoreDBClient(uri=eventstore_container.get_connection_url())
            ...     client.read_stream("test-stream", max_count=1)
            ... except StreamNotFound:
            ...     print("Server is accessible")
            ... except Exception as e:
            ...     print(f"Error connecting to server: {e}")
    """

    def __init__(
        self,
        image: str = "eventstore/eventstore:latest",
        http_port: int = 2113,
        tcp_port: int = 1113,
        cluster_size: int = 1,
        run_projections: str = "all",
        start_standard_projections: bool = true,
        insecure: bool = true,
        enable_atom_pub_over_http: bool = true,
        **kwargs,
    ) -> None:
        super(EventStoreContainer, self).__init__(image=image, **kwargs)
        self._command = "--insecure"
        self.ext_http_port = http_port or os.environ.get(
            "EVENTSTORE_EXT_HTTP_PORT", None
        )
        self.ext_tcp_port = tcp_port or os.environ.get("EVENTSTORE_EXT_TCP_PORT", None)
        self.cluster_size = cluster_size or os.environ.get("EVENTSTORE_CLUSTER_SIZE", 1)
        self.run_projections = run_projections or os.environ.get(
            "EVENTSTORE_RUN_PROJECTIONS", "all"
        )
        self.start_standard_projections = start_standard_projections or os.environ.get(
            "EVENTSTORE_START_STANDARD_PROJECTIONS", true
        )
        self.insecure = insecure or os.environ.get("EVENTSTORE_INSECURE", true)
        if self.insecure:
            raise RuntimeException(
                "Accessing secure EventStore clusters is currently unsupported"
            )
        self.enable_atom_pub_over_http = enable_atom_pub_over_http or os.environ.get(
            "EVENTSTORE_ENABLE_ATOM_PUB_OVER_HTTP", true
        )

        if self.ext_http_port:
            self.with_exposed_ports(self.ext_http_port)
        if self.ext_tcp_port:
            self.with_exposed_ports(self.ext_tcp_port)

    def _configure(self) -> None:
        self.with_env("EVENTSTORE_CLUSTER_SIZE", self.cluster_size)
        self.with_env("EVENTSTORE_RUN_PROJECTIONS", self.run_projections)
        self.with_env(
            "EVENTSTORE_START_STANDARD_PROJECTIONS", self.start_standard_projections
        )
        self.with_env("EVENTSTORE_EXT_TCP_PORT", self.ext_tcp_port)
        self.with_env("EVENTSTORE_EXT_HTTP_PORT", self.ext_http_port)
        self.with_env("EVENTSTORE_INSECURE", self.insecure)
        self.with_env(
            "EVENTSTORE_ENABLE_ATOM_PUB_OVER_HTTP", self.enable_atom_pub_over_http
        )

    def get_connection_url(self, host=None) -> str:
        if self.insecure:
            return f"esdb://localhost:{self.ext_http_port}?Tls=false"
        else:
            raise RuntimeException(
                "Accessing secure EventStore clusters is currently unsupported"
            )
