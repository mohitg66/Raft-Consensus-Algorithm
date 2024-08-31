all:
	make clean
	python open_terminal.py "make 0"
	python open_terminal.py "make 1"
	python open_terminal.py "make 2"
	python open_terminal.py "make 3"
	python open_terminal.py "make 4"
	python open_terminal.py "make client"

0:	
	python3 raft_server.py --node_id 0 --node_ip localhost --node_port 60000

1:
	python3 raft_server.py --node_id 1 --node_ip localhost --node_port 60001

2:
	python3 raft_server.py --node_id 2 --node_ip localhost --node_port 60002

3:
	python raft_server.py --node_id 3 --node_ip localhost --node_port 60003

4:
	python raft_server.py --node_id 4 --node_ip localhost --node_port 60004

client:
	python3 raft_client.py

clean:
	echo -n '' > logs_node_0/logs.txt
	echo -n '' > logs_node_0/metadata.txt
	echo -n '' > logs_node_0/dump.txt

	echo -n '' > logs_node_1/logs.txt
	echo -n '' > logs_node_1/metadata.txt
	echo -n '' > logs_node_1/dump.txt

	echo -n '' > logs_node_2/logs.txt
	echo -n '' > logs_node_2/metadata.txt
	echo -n '' > logs_node_2/dump.txt

	echo -n '' > logs_node_3/logs.txt
	echo -n '' > logs_node_3/metadata.txt
	echo -n '' > logs_node_3/dump.txt
	
	echo -n '' > logs_node_4/logs.txt
	echo -n '' > logs_node_4/metadata.txt
	echo -n '' > logs_node_4/dump.txt