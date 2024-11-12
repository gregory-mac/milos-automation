from annet.generators import BaseGenerator
from annet.storage import Storage

from . import description, hostname, shutdown, ip_addresses, rpl, bgp


def get_generators(store: Storage) -> list[BaseGenerator]:
    return [
        bgp.Bgp(store),
        description.Description(store),
        hostname.Hostname(store),
        ip_addresses.IpAddresses(store),
        rpl.RoutePolicy(store),
        shutdown.Shutdown(store),
    ]
