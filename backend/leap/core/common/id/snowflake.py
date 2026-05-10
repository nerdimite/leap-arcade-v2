import os
import threading
import time

# Snowflake algorithm constants
DEFAULT_EPOCH = 1735689600000  # Jan 1, 2025 00:00:00 UTC
NODE_ID_BITS = 10
SEQUENCE_BITS = 12
MAX_NODE_ID_VALUE = (1 << NODE_ID_BITS) - 1  # 2^10 - 1 = 1023
MAX_SEQUENCE_VALUE = (1 << SEQUENCE_BITS) - 1  # 2^12 - 1 = 4095
MILLISECONDS_MULTIPLIER = 1000


class SnowflakeIDGenerator:
    """
    Snowflake ID Generator implementation following Twitter's Snowflake algorithm.

    Generates 64-bit unique IDs with the following structure:
    - 1 bit: Sign bit (always 0)
    - 41 bits: Timestamp in milliseconds since custom epoch
    - 10 bits: Node ID (machine/process identifier)
    - 12 bits: Sequence number (incremented per ID within same millisecond)

    This allows for:
    - ~69 years of unique timestamps
    - 1024 unique nodes
    - 4096 IDs per millisecond per node
    """

    def __init__(self, node_id=None, epoch=DEFAULT_EPOCH):
        """
        Initialize the Snowflake ID Generator.

        Args:
            node_id: A unique identifier for the node (0-1023). If None, derives from process ID.
            epoch: Custom epoch timestamp in milliseconds (default: Jan 1, 2025 00:00:00 UTC).
        """
        # Set default node_id based on process ID if not provided
        if node_id is None:
            node_id = os.getpid() & MAX_NODE_ID_VALUE

        self.node_id = node_id
        self.epoch = epoch
        self.sequence = 0
        self.last_timestamp = -1

        # Bit allocation constants
        self.node_id_bits = NODE_ID_BITS
        self.sequence_bits = SEQUENCE_BITS

        # Maximum values for each component
        self.max_node_id = MAX_NODE_ID_VALUE
        self.max_sequence = MAX_SEQUENCE_VALUE

        # Bit shift positions
        self.node_id_shift = self.sequence_bits  # 12
        self.timestamp_shift = self.node_id_bits + self.sequence_bits  # 22

        # Thread safety lock
        self.lock = threading.Lock()

        # Validate node_id
        if self.node_id < 0 or self.node_id > self.max_node_id:
            raise ValueError(
                f"Node ID must be between 0 and {self.max_node_id}, got {self.node_id}"
            )

    def _current_timestamp(self):
        """Get current timestamp in milliseconds."""
        return int(time.time() * MILLISECONDS_MULTIPLIER)

    def _wait_for_next_millis(self, last_timestamp):
        """
        Wait until the next millisecond if sequence overflow occurs.

        Args:
            last_timestamp: The timestamp of the last generated ID.

        Returns:
            The next millisecond timestamp.
        """
        timestamp = self._current_timestamp()
        while timestamp <= last_timestamp:
            timestamp = self._current_timestamp()
        return timestamp

    def generate_id(self):
        """
        Generate a unique Snowflake ID.

        Returns:
            A 64-bit unique identifier as an integer.

        Raises:
            RuntimeError: If clock moves backwards.
        """
        with self.lock:
            timestamp = self._current_timestamp()

            # Check for clock regression
            if timestamp < self.last_timestamp:
                raise RuntimeError(
                    f"Clock moved backwards. Refusing to generate ID for "
                    f"{self.last_timestamp - timestamp} milliseconds"
                )

            # Same millisecond as last ID
            if timestamp == self.last_timestamp:
                # Increment sequence within the same millisecond
                self.sequence = (self.sequence + 1) & self.max_sequence

                # Sequence overflow - wait for next millisecond
                if self.sequence == 0:
                    timestamp = self._wait_for_next_millis(self.last_timestamp)
            else:
                # New millisecond - reset sequence
                self.sequence = 0

            # Update last timestamp
            self.last_timestamp = timestamp

            # Calculate timestamp offset from epoch
            timestamp_offset = timestamp - self.epoch

            # Construct the 64-bit ID
            snowflake_id = (
                (timestamp_offset << self.timestamp_shift)
                | (self.node_id << self.node_id_shift)
                | self.sequence
            )

            return snowflake_id

    def parse_id(self, snowflake_id):
        """
        Parse a Snowflake ID to extract its components.

        Args:
            snowflake_id: The Snowflake ID to parse.

        Returns:
            Dict containing timestamp, node_id, and sequence.
        """
        # Extract sequence (last 12 bits)
        sequence = snowflake_id & self.max_sequence

        # Extract node ID (next 10 bits)
        node_id = (snowflake_id >> self.node_id_shift) & self.max_node_id

        # Extract timestamp (remaining bits)
        timestamp_offset = snowflake_id >> self.timestamp_shift
        timestamp = timestamp_offset + self.epoch

        return {
            "timestamp": timestamp,
            "node_id": node_id,
            "sequence": sequence,
            "datetime": time.strftime(
                "%Y-%m-%d %H:%M:%S", time.gmtime(timestamp / MILLISECONDS_MULTIPLIER)
            ),
        }
