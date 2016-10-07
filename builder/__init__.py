from adapters.certuk_mod.builder.custom_observables.http_session import HTTPSessionObservableDefinition
from adapters.certuk_mod.builder.custom_observables.network_connection import NetworkConnectionObservableDefinition
from adapters.certuk_mod.builder.custom_observables.port import PortObservableDefinition


CUSTOM_OBSERVABLES = (
    HTTPSessionObservableDefinition(),
    NetworkConnectionObservableDefinition(),
    PortObservableDefinition()
)



