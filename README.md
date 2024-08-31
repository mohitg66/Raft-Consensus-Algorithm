# Raft Consensus Algorithm Implementation

This project implements the Raft consensus algorithm in Python using gRPC for communication between nodes. The Raft algorithm is used to manage a replicated log and ensure consistency across distributed systems.


## Getting Started

### Prerequisites

- Python 3.x
- gRPC
- Protobuf

### Installation and Running the Project

1. Clone the repository:
    ```sh
    git clone github.com/mohitg66/Raft-Consensus-Algorithm.git
    cd Raft-Consensus-Algorithm
    ```

2. Install the required Python packages:
    ```sh
    pip install -r requirements.txt
    ```

3. Generate gRPC code from the protobuf file:
    ```sh
    python -m grpc_tools.protoc -I. --python_out=. --pyi_out=. --grpc_python_out=. raft.proto
    ```

4. Clear logs:
    ```sh
    make clean      # Optional, to clear logs
    ```

5. Start the server nodes:
    ```sh
    make 0          # On 1st terminal
    make 1          # On 2nd terminal
    make 2          # On 3rd terminal
    make 3          # On 4th terminal
    make 4          # On 5th terminal
    ```

6. Start the client:
    ```sh
    make client     # On a new terminal
    ```


## Code Overview

### `raft_server.py`
- Contains the main server implementation.
- Defines the `RaftNode` class which implements the Raft consensus algorithm.
- Handles RPC methods such as `AppendEntry`, `RequestVote`, and `ServeClient`.

### `raft_client.py`
- Contains the client implementation to interact with the Raft cluster.

### `raft.proto`
- Defines the protobuf messages and gRPC services for the Raft algorithm.


## Acknowledgements

- [Raft Consensus Algorithm](https://raft.github.io/)
- [gRPC](https://grpc.io/)
- [Protocol Buffers](https://developers.google.com/protocol-buffers)