while retry < num_retries:
    try:
        client.connect(node_list.get(cur_node)[0],
                username = username, password = password,
                port = ssh_port)
        scp = SCPClient(client.get_transport())
        scp.put(scheduler_file, dir_remote)
        scp.put(source_central_file, dir_remote_profiler)
        scp.close()
        print('File transfer complete to ' + cur_node + '\n')
        break
    except (paramiko.ssh_exception.NoValidConnectionsError, gaierror):
        print('SSH Connection refused, will retry in 2 seconds')
        time.sleep(2)
        retry += 1
