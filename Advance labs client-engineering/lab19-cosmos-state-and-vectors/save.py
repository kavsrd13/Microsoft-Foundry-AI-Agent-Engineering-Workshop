from dotenv import load_dotenv
load_dotenv()

from store import container, signed_in_partition

user = signed_in_partition()
state = container('sessions')
state.upsert_item({'id':'session-1', 'userId':user, 'ttl':3600,
                   'messages':[{'role':'user','content':'My synthetic case is ACME-204.'}]})
state.upsert_item({'id':'preferences', 'userId':user, 'ttl':86400,
                   'language':'English', 'style':'short answers'})
print('Saved one-hour conversation and one-day preference. Exit this process now.')
