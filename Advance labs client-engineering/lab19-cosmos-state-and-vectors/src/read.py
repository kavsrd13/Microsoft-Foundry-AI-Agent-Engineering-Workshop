from store import container, signed_in_partition

state = container('sessions')
user = signed_in_partition()
print(state.read_item(item='session-1', partition_key=user)['messages'])
print(state.read_item(item='preferences', partition_key=user)['style'])
print('Recovered from Cosmos in a new process.')
