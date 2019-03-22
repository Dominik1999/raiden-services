"""
The tests in this module mock events creation by using a mock blockchain listener.

This makes them a lot faster than using full blockchain based approach and they should
be used most of the time to keep test times short.
"""
from typing import List

from pathfinding_service import PathfindingService
from pathfinding_service.model import TokenNetwork
from raiden.messages import UpdatePFS
from raiden_libs.types import Address, ChannelIdentifier

# Mock a valid UpdatePFS message
valid_balance_update = UpdatePFS
valid_balance_update.nonce =

# Mock an invalid UpdatePFS message

def test_pfs_with_mocked_events(
    token_network_model: TokenNetwork,
    addresses: List[Address],
    pathfinding_service_mocked_listeners: PathfindingService,
    channel_descriptions_case_1: List,
):
    registry_listener = pathfinding_service_mocked_listeners.token_network_registry_listener
    # assert registry_listener

    token_network_address = token_network_model.address

    # this is a new pathfinding service, there should be no token networks registered
    assert len(pathfinding_service_mocked_listeners.token_networks.keys()) == 0

    # emit a TokenNetworkCreated event
    registry_listener.emit_event(dict(
        event='TokenNetworkCreated',
        blockNumber=12,
        args=dict(
            token_network_address=token_network_address,
            token_address=token_network_model.token_address,
        ),
    ))

    # now there should be a token network registered
    assert token_network_address in pathfinding_service_mocked_listeners.token_networks
    token_network = pathfinding_service_mocked_listeners.token_networks[token_network_address]

    assert len(pathfinding_service_mocked_listeners.token_network_listeners) == 1
    network_listener = pathfinding_service_mocked_listeners.token_network_listeners[0]

    # We try to send a balance update before initializing the channels
    PathfindingService.handle_message(valid_balance_update)

    assert

    # Now initialize some channels in this network.
    for index, (
        p1_index,
        p1_deposit,
        p1_capacity,
        _p1_fee,
        p1_reveal_timeout,
        p2_index,
        p2_deposit,
        p2_capacity,
        _p2_fee,
        p2_reveal_timeout,
        settle_timeout,
    ) in enumerate(channel_descriptions_case_1):
        network_listener.emit_event(dict(
            address=token_network_address,
            event='ChannelOpened',
            args=dict(
                channel_identifier=index,
                participant1=addresses[p1_index],
                participant2=addresses[p2_index],
                settle_timeout=settle_timeout,
            ),
        ))

        network_listener.emit_event(dict(
            address=token_network_address,
            event='ChannelNewDeposit',
            args=dict(
                channel_identifier=index,
                participant=addresses[p1_index],
                total_deposit=p1_deposit,
            ),
        ))

        network_listener.emit_event(dict(
            address=token_network_address,
            event='ChannelNewDeposit',
            args=dict(
                channel_identifier=index,
                participant=addresses[p2_index],
                total_deposit=p2_deposit,
            ),
        ))

    # now there should be seven channels
    assert len(token_network.channel_id_to_addresses.keys()) == 7
    # check that deposits got registered
    for index, (
        p1_index,
        p1_deposit,
        _p1_capacity,
        _p1_fee,
        _p1_reveal_timeout,
        p2_index,
        p2_deposit,
        _p2_capacity,
        _p2_fee,
        _p2_reveal_timeout,
        _settle_timeout,
    ) in enumerate(channel_descriptions_case_1):
        p1, p2 = token_network.channel_id_to_addresses[ChannelIdentifier(index)]
        assert p1 == addresses[p1_index]
        assert p2 == addresses[p2_index]

        view1 = token_network.G[p1][p2]['view']
        view2 = token_network.G[p2][p1]['view']

        assert view1.deposit == p1_deposit
        assert view2.deposit == p2_deposit

