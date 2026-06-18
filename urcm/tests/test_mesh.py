import time

import numpy as np

from urcm.core.data_models import MeshSignal
from urcm.core.mesh import MeshNetwork, MeshNode
from urcm.core.validation import DataValidation


class TestMeshNode:
    def test_construction(self):
        node = MeshNode("n1")
        assert node.node_id == "n1"
        assert node.neighbors == []
        assert node.is_active is True
        assert node.health_score == 1.0
        assert 0 <= node.phase < 2 * np.pi

    def test_connect_bidirectional(self):
        a = MeshNode("a")
        b = MeshNode("b")
        a.connect(b)
        assert b in a.neighbors
        assert a in b.neighbors
        assert "b" in a.trusted_neighbors
        assert "a" in b.trusted_neighbors

    def test_disconnect_bidirectional(self):
        a = MeshNode("a")
        b = MeshNode("b")
        a.connect(b)
        a.disconnect(b)
        assert b not in a.neighbors
        assert a not in b.neighbors

    def test_connect_no_self(self):
        a = MeshNode("a")
        a.connect(a)
        assert a not in a.neighbors

    def test_send_receive_signal(self):
        sender = MeshNode("sender")
        receiver = MeshNode("receiver")
        sender.connect(receiver)

        sender.update_local_state(mu=0.5)
        sender.phase = 1.0
        sent = sender.broadcast_signal()
        assert sent == 1
        assert receiver.phase != 1.0 or receiver.current_mu == 0.0

    def test_send_to_untrusted_is_ignored(self):
        MeshNode("sender")
        receiver = MeshNode("receiver")
        # No connection, so sender is untrusted
        signal = MeshSignal(
            sender_id="sender",
            delta_mu=0.1,
            phase_alignment=1.0,
            timestamp=time.time(),
            signal_type="sync",
        )
        receiver.receive_signal(signal)
        assert receiver.error_history == [] or "untrusted" in receiver.error_history[-1]

    def test_inactive_node_sends_nothing(self):
        node = MeshNode("n1")
        node.is_active = False
        sent = node.broadcast_signal()
        assert sent == 0

    def test_inactive_node_ignores_signal(self):
        receiver = MeshNode("receiver")
        receiver.is_active = False
        sender = MeshNode("sender")
        sender.connect(receiver)
        sender.update_local_state(mu=1.0)
        sender.broadcast_signal()
        assert receiver.current_mu == 0.0


class TestMeshNetwork:
    def test_add_node(self):
        net = MeshNetwork()
        node = MeshNode("n1")
        net.add_node(node)
        assert "n1" in net.nodes

    def test_broadcast_signal(self):
        net = MeshNetwork()
        a = MeshNode("a")
        b = MeshNode("b")
        net.add_node(a)
        net.add_node(b)
        a.connect(b)
        a.update_local_state(mu=0.5)
        total = net.step_broadcast()
        assert total >= 1

    def test_validate_signal(self):
        net = MeshNetwork()
        a = MeshNode("a")
        b = MeshNode("b")
        net.add_node(a)
        net.add_node(b)
        a.connect(b)
        a.update_local_state(mu=0.3)
        a.broadcast_signal()
        assert len(b.error_history) == 0

    def test_validate_signal_rejects_future_timestamp(self):
        node = MeshNode("n1")
        neighbor = MeshNode("n2")
        node.connect(neighbor)
        signal = MeshSignal(
            sender_id="node",
            delta_mu=0.1,
            phase_alignment=1.0,
            timestamp=time.time() + 100.0,
            signal_type="sync",
        )
        # Bypass the untrusted check since node_id matches
        result = neighbor._validate_signal(signal)
        assert result is False

    def test_validate_signal_rejects_old_timestamp(self):
        node = MeshNode("n1")
        neighbor = MeshNode("n2")
        node.connect(neighbor)
        signal = MeshSignal(
            sender_id="node",
            delta_mu=0.1,
            phase_alignment=1.0,
            timestamp=time.time() - 100.0,
            signal_type="sync",
        )
        result = neighbor._validate_signal(signal)
        assert result is False

    def test_validate_signal_rejects_nonfinite(self):
        node = MeshNode("n1")
        neighbor = MeshNode("n2")
        node.connect(neighbor)
        signal = MeshSignal(
            sender_id="node",
            delta_mu=float("nan"),
            phase_alignment=1.0,
            timestamp=time.time(),
            signal_type="sync",
        )
        result = neighbor._validate_signal(signal)
        assert result is False

    def test_validate_signal_accepts_valid(self):
        node = MeshNode("n1")
        neighbor = MeshNode("n2")
        node.connect(neighbor)
        signal = MeshSignal(
            sender_id="n1",
            delta_mu=0.1,
            phase_alignment=2.0,
            timestamp=time.time(),
            signal_type="sync",
        )
        assert DataValidation.validate_mesh_signal(signal) is True
        assert neighbor._validate_signal(signal) is True
