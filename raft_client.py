import grpc
import raft_pb2
import raft_pb2_grpc
from concurrent import futures

class Client:
    def __init__(self):
        self.nodes = [('localhost', '50000'), ('localhost', '50001'), ('localhost', '50002'), ('localhost', '50003'), ('localhost', '50004')]
        # self.nodes = [('34.31.238.13', '50000'), ('34.66.170.177', '50001'), ('34.170.205.12', '50002'), ('35.225.176.218', '50003'), ('34.131.12.182', '50004')]
        self.current_leader = {
            "ip": None,
            "port": None
        }

    def send_request_to_leader(self, request, leader_ip, leader_port):
        channel = grpc.insecure_channel(leader_ip + ':' + leader_port)
        stub = raft_pb2_grpc.RaftServiceStub(channel)
        request_message = raft_pb2.ClientRequest(
            operation=request.operation,
            key=request.key,
            value=request.value
        )
        try:
            response = stub.ServeClient(request_message)
        except grpc.RpcError as e:
            print("Problem in sending request to the leader")
            return None
        return response

    def send_request(self, request):

        try:
            if self.current_leader["ip"] != None and self.current_leader["port"] != None:
                leader_ip = self.current_leader["ip"]
                leader_port = self.current_leader["port"]

                response = self.send_request_to_leader(request, leader_ip, leader_port)
                if response:
                    if response.success:
                        print("Request processed successfully.")
                        print(f"Leader: {response.leader_id}")
                        print("data: ", response.data)
                    else:
                        for i in self.nodes:
                            leader_ip = i[0]  # Accessing IP
                            leader_port = i[1]  # Accessing port
                            response = self.send_request_to_leader(request, leader_ip, leader_port)
                            if response:
                                if response.success:
                                    print("Request processed successfully.")
                                    if response.leader_id == '1':
                                        self.current_leader["ip"] = 'localhost'
                                        self.current_leader["port"] = '50001'
                                    elif response.leader_id == '2':
                                        self.current_leader["ip"] = 'localhost'
                                        self.current_leader["port"] = '50002'
                                    elif response.leader_id == '3':
                                        self.current_leader["ip"] = 'localhost'
                                        self.current_leader["port"] = '50003'
                                    print(f"Leader: {response.leader_id}")
                                    print("data: ", response.data)
                                    break
                                else:
                                    print("Error: Request failed.")
                else:
                    for i in self.nodes:
                        leader_ip = i[0]  # Accessing IP
                        leader_port = i[1]  # Accessing port
                        response = self.send_request_to_leader(request, leader_ip, leader_port)
                        if response:
                            if response.success:
                                print("Request processed successfully.")
                                if response.leader_id == '1':
                                    self.current_leader["ip"] = 'localhost'
                                    self.current_leader["port"] = '50001'
                                elif response.leader_id == '2':
                                    self.current_leader["ip"] = 'localhost'
                                    self.current_leader["port"] = '50002'
                                elif response.leader_id == '3':
                                    self.current_leader["ip"] = 'localhost'
                                    self.current_leader["port"] = '50003'
                                print(f"Leader: {response.leader_id}")
                                print("data: ", response.data)
                                break
                            else:
                                print("Error: Request failed.")
                                    
            else:
                for i in self.nodes:
                    leader_ip = i[0]  # Accessing IP
                    leader_port = i[1]  # Accessing port
                    response = self.send_request_to_leader(request, leader_ip, leader_port)
                    if response:
                        if response.success:
                            print("Request processed successfully.")
                            if response.leader_id == '1':
                                self.current_leader["ip"] = 'localhost'
                                self.current_leader["port"] = '50001'
                            elif response.leader_id == '2':
                                self.current_leader["ip"] = 'localhost'
                                self.current_leader["port"] = '50002'
                            elif response.leader_id == '3':
                                self.current_leader["ip"] = 'localhost'
                                self.current_leader["port"] = '50003'
                            print(f"Leader: {response.leader_id}")
                            print("data: ", response.data)
                            break
                        else:
                            print("Error: Request failed.")
        except:
            print("Problem in sending the request to leader using gRPC")

class ClientNotificationServer(raft_pb2_grpc.RaftServiceServicer):
    def ReceiveInfo(self, request, context):
        # Process the request and send response
        print(f"Received notification from node {request.data}")
        pass

class Request:
    def __init__(self, operation, key, value):
        self.operation = operation
        self.key = key
        self.value = value

def display_menu():
    print("RAFT Client Menu")
    print("1. Send Request")
    print("2. Exit")

def get_menu_choice():
    try: 
        choice = input("Enter your choice: ")
        return int(choice)
    except:
        print("Integer choice please!")

def get_request_details():
    try:
        operation = input("Enter operation: ")
        key = input("Enter key: ")
        if operation == "SET":
            value = input("Enter value: ")
        else:
            value = None
        return Request(operation, key, value)
    except:
        print("Invalid request, try again!")

def run_client_instance():
    client = Client()
    
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    raft_pb2_grpc.add_RaftServiceServicer_to_server(ClientNotificationServer(), server)
    server.add_insecure_port('localhost:60010')
    server.start()
    print("Client notification server started on port 60010")

    while True:
        display_menu()
        choice = get_menu_choice()
        try:
            if choice == 1:
                request = get_request_details()
                client.send_request(request)
            elif choice == 2:
                print("Exiting...")
                break
            else:
                print("Invalid choice. Please try again.")
        except:
            print("Renter the choice")

    # server.wait_for_termination()

if __name__ == "__main__":
    run_client_instance()