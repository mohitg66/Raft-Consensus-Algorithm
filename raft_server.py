import grpc
import raft_pb2
import raft_pb2_grpc
import threading
import argparse
from random import randint
from concurrent import futures
import threading
import pickle
import time
import os

def print1(*args, **kwargs):
    args1 = parse_args()
    file_name = f'logs_node_{args1.node_id}/dump.txt'

    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(file_name), exist_ok=True)

    with open(file_name, 'a') as file:
        # Convert all arguments to strings and write to the file
        file.write(' '.join(map(str, args)) + '\n')

    # Print the arguments to the console
    print(*args)
        

class Timeout:
    def __init__(self, election_timeout_seconds, callback, purpose):
        self.election_timeout_seconds = election_timeout_seconds
        self.callback = callback
        self.purpose = purpose
        self.timer = None

    def start(self):
        if self.purpose == "election_timeout":
            self.election_timeout_seconds = randint(5, 10)
        print1(f"{self.purpose} started for t = ", self.election_timeout_seconds)
        self.timer = threading.Timer(self.election_timeout_seconds, self.callback)
        self.timer.start()

    def cancel(self):
        if self.timer:
            self.timer.cancel()

    def reset(self):
        self.cancel()
        self.start()

class RaftNode(raft_pb2_grpc.RaftServiceServicer):

    def update_metadata(self):
        file_name = f'logs_node_{self.node_id}/metadata.txt'
        with open(file_name, 'w') as file:
            file.write(f"commit_index: {self.commit_index}\n")
            file.write(f"term: {self.term}\n")
            file.write(f"voted_for: {self.voted_for}\n")

    def load_metadata(self):
        # return commit_index, term, voted_for
        file_name = f'logs_node_{self.node_id}/metadata.txt'
        try:
            with open(file_name, 'r') as file:
                lines = file.readlines()
                commit_index = lines[0].split()[-1]
                term = lines[1].split()[-1]
                voted_for = lines[2].split()[-1]
                if voted_for == 'None':
                    voted_for = None
                return int(commit_index), int(term), voted_for
        except:
            return 0, 0, None
    
    def __init__(self, node_id, node_ip, node_port):
        self.node_id = node_id
        self.node_ip = node_ip
        self.node_port = node_port
        self.nodes = [('localhost', "60000"), ('localhost', "60001"), ('localhost', "60002"), ('localhost', "60003"), ('localhost', "60004")]
        self.another_port = node_port - 10000

        # self.commit_index = 0 
        # self.term = 0
        # self.voted_for = None
        self.commit_index, self.term, self.voted_for = self.load_metadata()
        self.state = 'follower'
        self.logs = self.read_logs_from_file(f'logs_node_{self.node_id}/logs.txt') 
        self.last_log_index = 0
        self.last_log_term = 0
        # self.prev_log_index = 0
        self.prev_log_index= [0 for i in range(len(self.nodes))]
        self.prev_log_term = [0 for i in range(len(self.nodes))]
        self.database = dict()

        self.heartbeat_timeout = None
        self.election_timeout = None
        self.folder = f'logs_node_{self.node_id}'
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)
        self.leader_lease_remaining_time = None
        self.leader_lease_timeout = None
        self.node_id_with_lease = None
        self.successful_heartbeats= [False for i in range(len(self.nodes))]

        raft_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        raft_pb2_grpc.add_RaftServiceServicer_to_server(self, raft_server)
        raft_server.add_insecure_port(f'{self.node_ip}:{self.node_port}')
        raft_server.add_insecure_port(f'{self.node_ip}:{self.another_port}')
        raft_server.start()
        print1(f"Raft node {self.node_id} started on port {self.node_port} and {self.another_port}.")

        self.set_election_timeout()
        
        raft_server.wait_for_termination()  

    def write_logs_to_file(self, logs, file_name):
        with open(file_name, 'w') as file:
            for key, value in logs.items():
                entry_str = ' '.join(str(e) for e in value['entry'])
                line = f"{entry_str} {value['term']}\n"
                file.write(line)    

    def read_logs_from_file(self, file_name):
        logs = dict()
        try:
            with open(file_name, 'r') as file:
                for line in file:
                    parts = line.strip().split()
                    term = int(parts[-1])
                    entry = (parts[0], parts[1], ' '.join(parts[2:-1]))
                    key = len(logs) + 1
                    logs[key] = {'term': term, 'entry': entry}
                return logs
        except:
            return dict()

    def ServeClient(self, request, context):
        print1(f"Node {self.node_id}({self.state}) received {request.operation}client request.")
        data = str()
        leader_id = str()
        success = False
        if self.state != 'leader':
            leader_id = str(self.node_id_with_lease)
            success = False
        elif self.state == 'leader':
            leader_id = str(self.node_id)
            if request.operation == "GET":
                if request.key in self.database:
                    data = self.database[request.key]
                    success = True
                else:
                    success = False
            elif request.operation == "SET":
                self.logs[len(self.logs) + 1 if self.logs else 1] = {'term': self.term, 'entry': (request.operation, request.key, request.value)}
                # write to log file
                self.write_logs_to_file(self.logs, self.folder + '/logs.txt')
                success = True
        
        return raft_pb2.ServeClientReply(data=data, success=success, leader_id=leader_id)

    def set_election_timeout(self):
        if self.election_timeout is not None:
            self.election_timeout.reset()
        else:
            election_timeout_seconds = randint(5, 10)
            self.election_timeout = Timeout(election_timeout_seconds, self.start_election, "election_timeout")
            self.election_timeout.start()

    def set_heartbeat_timeout(self):
        if self.heartbeat_timeout is not None:
            self.heartbeat_timeout.reset()
        else:
            self.heartbeat_timeout = Timeout(1, self.send_heartbeat, "heartbeat_timeout")
            self.heartbeat_timeout.start()
        
    def callback_leader_lease_timeout(self):
        print1(f"Node {self.node_id}({self.state}) lease timeout")
        if self.state == 'leader':
            self.state = 'follower'
            self.voted_for = None
            self.set_election_timeout()
            print1(f"Stepping Down!\nNode {self.node_id}({self.state}) transitions to follower state for term {self.term}")
            self.leader_lease_remaining_time = None
            self.leader_lease_timeout = None
            self.node_id_with_lease = None
        else:
            self.leader_lease_remaining_time = None
            self.leader_lease_timeout = None
            self.node_id_with_lease = None

    def set_leader_lease_timeout(self, remaining_time=10):
        if self.leader_lease_timeout is not None:
            self.leader_lease_timeout.reset()
        else:
            self.leader_lease_timeout = Timeout(remaining_time, self.callback_leader_lease_timeout, "leader_lease_timeout")
            self.leader_lease_timeout.start() 
        self.leader_lease_remaining_time = remaining_time

    def start_election(self):
        print1(f"Node {self.node_id}({self.state}) timed out for term {self.term}. Starting Election\n")
        if self.state != 'leader':
            self.state = 'candidate'
            self.term += 1
            self.votes_received = 1
            self.set_election_timeout()
            print1(f"Node {self.node_id}({self.state}) transitions to candidate state for term {self.term}")
            self.voted_for = self.node_id
            print1(f"Node {self.node_id}({self.state}) voted for itself.")
            for node_ip, node_port in self.nodes:
                if node_port != str(self.node_port) and self.state != 'leader':
                    print1(f"Node {self.node_id}({self.state}) sending RequestVote RPC to {node_port}.")
                    channel = grpc.insecure_channel(node_ip + ':' + node_port)
                    stub = raft_pb2_grpc.RaftServiceStub(channel)
                    request_vote_args = raft_pb2.RequestVoteArgs(
                        term=self.term,
                        candidate_id=self.node_id,
                        last_log_index = len(self.logs) if self.logs else 0,
                        last_log_term = self.logs[len(self.logs)]['term'] if self.logs else 0
                    )
                    response= None
                    try: response = stub.RequestVote(request_vote_args)
                    except grpc.RpcError as e: print1(f"Error sending RequestVote RPC to {node_ip + ':' + node_port}")

                    if response is not None:
                        if response.vote_granted:
                            print1(f"Vote Granted! \nNode {self.node_id}({self.state}) received vote from {node_port}.")
                            self.votes_received += 1
                            self.check_votes()
                        else:
                            print1(f"Vote Denied!\nNode {self.node_id}({self.state}) recieved False vote from {node_port}.")
                            # step down to follower
                            
                    else:
                        print1(f"Node {self.node_id}({self.state}) received no response from {node_port}.")

    def RequestVote(self, request, context):
        candidate_id = request.candidate_id
        term = request.term
        last_log_index = request.last_log_index
        last_log_term = request.last_log_term
        response = self.request_vote_rpc(term, candidate_id, last_log_index, last_log_term)
        return raft_pb2.RequestVoteReply(term=response["term"], vote_granted=response["vote_granted"])
        
    def request_vote_rpc(self, term, candidate_id, last_log_index, last_log_term):
        print1(f"Node {self.node_id}({self.state}) received RequestVote RPC from {candidate_id}.")

        if term < self.term:
            return {
                "term": self.term,
                "vote_granted": False
            }
        
        if self.voted_for is None or self.voted_for == candidate_id:
            if last_log_term >= self.last_log_term and last_log_index >= self.last_log_index:
                self.voted_for = candidate_id
                self.state = 'follower'
                self.term = term
                print1(f"Node {self.node_id}({self.state}) voted for {candidate_id}.")
                self.set_election_timeout()
                return {
                    "term": self.term,
                    "vote_granted": True
                }
            
        
        if term > self.term and last_log_index >= self.last_log_index and last_log_term >= self.last_log_term and self.voted_for == self.node_id:
            self.state = 'follower'
            self.voted_for = candidate_id
            self.term = term
            print1(f"Node {self.node_id}({self.state}) voted for {candidate_id}.")
            self.set_election_timeout()
            return {
                "term": self.term,
                "vote_granted": True
            }
    
    def check_votes(self):
        if self.state == 'candidate':
            if self.votes_received > len(self.nodes) / 2:
                if self.election_timeout is not None:
                    self.election_timeout.cancel()
                    self.election_timeout = None
                
                if self.leader_lease_timeout is not None:
                    print1(f'Waiting for leader_lease_node: {self.node_id_with_lease}, remaining time: {self.leader_lease_remaining_time}')
                    while self.leader_lease_remaining_time != None:
                        print1(f'Waiting for leader_lease_node: {self.node_id_with_lease}')
                        time.sleep(1)

                print1(f"Node {self.node_id}({self.state}) became the leader for term {self.term}")
                self.state = 'leader'
                self.votes_received = 0
                self.node_id_with_lease = self.node_id
                self.logs[len(self.logs) + 1 if self.logs else 1] = {'term': self.term, 'entry': ('NO-OP', '', '')}
                self.write_logs_to_file(self.logs, self.folder + '/logs.txt')
                self.set_heartbeat_timeout()
                self.set_leader_lease_timeout()

    def handleAppendEntriesResponse(self, stub, response, i):
        if response is None:
            return -1
        
        self.successful_heartbeats[i] = True
        
        if response.success:
            self.prev_log_index[i] = len(self.logs)
            self.prev_log_term[i] = self.logs[self.prev_log_index[i]]['term']
        else:
            if response.term > self.term:
                self.state = 'follower'
                self.term = response.term
                self.voted_for = None
                self.set_election_timeout()
            
            else:
                self.prev_log_index[i] -= 1
                nextIndex = self.prev_log_index[i] +1
                if nextIndex < 1:
                    return
                else:
                    entries = []
                    for i in range(nextIndex, len(self.logs) + 1):
                        log_entry = raft_pb2.LogEntry(operation= self.logs[i]['entry'][0], 
                                                    key= self.logs[i]['entry'][1], 
                                                    value= self.logs[i]['entry'][2], 
                                                    term= self.logs[i]['term'], 
                                                    index= i)
                        entries.append(log_entry)

                    append_entries_args = raft_pb2.AppendEntryArgs(
                        term=self.term,
                        leader_id= self.node_id,
                        prev_log_index= self.prev_log_index[i],
                        prev_log_term= self.logs[self.prev_log_index[i]]['term'],
                        entries=entries,
                        leader_commit= self.commit_index,
                        lease_duration= 10
                    )

                    try:
                        print1(f"Node {self.node_id}({self.state}) sent AppendEntries RPC to {self.nodes[i][0] + ':' + self.nodes[i][1]}.")
                        response = stub.AppendEntry(append_entries_args)
                        self.handleAppendEntriesResponse(stub, response, i)
                    except grpc.RpcError as e:
                        print1(f"Error occured sending AppendEntries RPC to {self.nodes[i][0] + ':' + self.nodes[i][1]}")
                        return 1

    def send_heartbeat_to_nodes(self, i):
        node_ip, node_port = self.nodes[i]
        nextIndex= self.prev_log_index[i] + 1
        entries = []
        for idx in range(nextIndex, len(self.logs) + 1):
            log_entry = raft_pb2.LogEntry(operation= self.logs[idx]['entry'][0], 
                                           key= self.logs[idx]['entry'][1], 
                                           value= self.logs[idx]['entry'][2], 
                                           term= self.logs[idx]['term'], 
                                           index= idx)
            entries.append(log_entry)

        channel = grpc.insecure_channel(node_ip + ':' + node_port)
        stub = raft_pb2_grpc.RaftServiceStub(channel)
        append_entries_args = raft_pb2.AppendEntryArgs(
            term=self.term,
            leader_id= self.node_id,
            prev_log_index= self.prev_log_index[i],
            prev_log_term= self.logs[self.prev_log_index[i]]['term'] if self.prev_log_index[i] > 0 else 0,
            entries=entries,
            leader_commit= self.commit_index,
            lease_duration= 10
        )

        try:
            print1(f"Node {self.node_id}({self.state}) sent AppendEntries RPC to {node_ip + ':' + node_port}.")
            response = stub.AppendEntry(append_entries_args)
            # use if-else to handle responses directly, or use a function
            retVal = self.handleAppendEntriesResponse(stub, response, i)
                    
        except grpc.RpcError as e:
            print1(f"Error sending AppendEntries RPC to {node_ip + ':' + node_port}")
            return
        
    def send_heartbeat(self):
        print1()
        if self.state == 'leader':
            # self.set_leader_lease_timeout()
            acked = 1
            threads = []

            self.successful_heartbeats= [False for i in range(len(self.nodes))]
            # avoid threading for now
            for i in range(len(self.nodes)):
                if i==self.node_id:
                    self.successful_heartbeats[i] = True
                    continue
                self.send_heartbeat_to_nodes(i)
            
            # if response from heartbeat was successful, only then reset the leader's lease thread
            if sum(self.successful_heartbeats) > len(self.nodes) / 2:
                self.set_leader_lease_timeout()

                # commit
                if self.logs is not None:
                    for i in range(2, len(self.logs) + 1):
                        if self.logs[i]['entry'][0] != 'NO-OP':
                            self.database[self.logs[i]['entry'][1]] = self.logs[i]['entry'][2]
                        self.commit_index = i

            #  write to log file, and metadata
            self.write_logs_to_file(self.logs, self.folder + '/logs.txt')
            self.update_metadata()

            self.set_heartbeat_timeout()
            print1("database: ", self.database)   

    def AppendEntry(self, request, context):
        print1()
        self.voted_for = None
        # print1(f"Node {self.node_id}({self.state}) received AppendEntries RPC from {request.leader_id}: \n{request}")
        print1(f"Node {self.node_id}({self.state}) received AppendEntries RPC from {request.leader_id}")

        # invalid leader: shorter term
        if request.term < self.term:
            print1(f"Node {self.node_id}({self.state}) rejected AppendEntries RPC from {request.leader_id} due to invalid leader")
            return raft_pb2.AppendEntryReply(term=self.term, success=False)   

        # valid leader: longer term or same term
        else:
            self.state = 'follower'

            self.set_election_timeout()
            self.set_leader_lease_timeout(request.lease_duration)
            
            if request.prev_log_index > len(self.logs) if self.logs else 0:
                self.term = request.term
                print1(f"Node {self.node_id}({self.state}) replied False to AppendEntries RPC from {request.leader_id} due to outdated logs")
                
                self.update_metadata()
                return raft_pb2.AppendEntryReply(term=self.term, success=False)   

            elif request.prev_log_index > 0 and self.logs[request.prev_log_index]['term'] != request.prev_log_term:
                self.term = request.term
                for i in range(request.prev_log_index, len(self.logs)):
                    del self.logs[i]
                print1(f"Node {self.node_id}({self.state}) replied False to AppendEntries RPC from {request.leader_id} due to log inconsistency")
                
                self.update_metadata()
                return raft_pb2.AppendEntryReply(term=self.term, success=False)   
            
            else:
                self.term = request.term
                if request.entries is not None:
                    for entry in request.entries:
                        self.logs[entry.index] = {'term': entry.term, 'entry': (entry.operation, entry.key, entry.value)}
                        self.last_log_index = entry.index
                        self.last_log_term = entry.term

                if request.leader_commit > self.commit_index:
                    self.commit_index = min(request.leader_commit, self.prev_log_index[self.node_id])

                # write to log file
                self.write_logs_to_file(self.logs, self.folder + '/logs.txt')

                # self.set_election_timeout()
                # self.set_leader_lease_timeout(request.lease_duration)
                
                print1(f"Node {self.node_id}({self.state}) accepted AppendEntries RPC from {request.leader_id}")

                self.update_metadata()
                return raft_pb2.AppendEntryReply(term=self.term, success=True)
        
def parse_args():
    parser = argparse.ArgumentParser(description='Raft Node')
    parser.add_argument('--node_id', type=int, default=0, help='Node ID')
    parser.add_argument('--node_ip', type=str, default='localhost', help='Node IP address')
    parser.add_argument('--node_port', type=int, default=60000, help='Node port')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    raft_service = RaftNode(args.node_id, args.node_ip, args.node_port)

'''
to run:
clear logs:
make

server nodes:
python raft_server_mohit.py --node_id 0 --node_ip localhost --node_port 60000
python raft_server_mohit.py --node_id 1 --node_ip localhost --node_port 60001
.
.

client:
python raft_client.py
'''