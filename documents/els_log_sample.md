# Serched ELS Log Message Sample
```python
es = Elasticsearch()
results = es.search(~)
results['hits']['hits']
```
=> results
```json
sample = {'_index': '.ds-filebeat-8.13.2-2024.04.15-000001',
          '_type': '_doc', '_id': '6eSH744BE8ONC02o8ryd',
          '_score': None,
          '_source': {
              '@timestamp': '2024-04-18T04:47:17.885Z',
              'agent': {
                  'type': 'filebeat', 'version': '8.13.2', 'ephemeral_id': 'd7f5a404-6e8c-4131-af09-30d19b018a74', 'id': '888a1335-0450-4f87-aa2e-f333bd4aceac', 'name': 'backend-imageproxy01-vm'
              },
              'log': {
                  'log': '13:47:11.086 [lettuce-nioEventLoop-6-2] INFO  i.l.c.protocol.ReconnectionHandler Reconnected to dev-redis-01.koreacentral.cloudapp.azure.com/<unresolved>:25286\n',
                  'stream': 'stdout',
                  'time': '2024-04-18T04:47:11.0862656Z',
                  'thread': '[lettuce-nioEventLoop-6-2]',
                  'level': 'INFO',
                  'timestamp': '13:47:11.086'
              },
              'input': {'type': 'filestream'},
              'ecs': {'version': '8.0.0'},
              'host': {
                  'mac': ['00-22-48-6C-C4-08', '02-42-80-7B-6D-03', '2A-9A-44-C8-65-6E'],
                  'hostname': 'backend-imageproxy01-vm',
                  'architecture': 'x86_64',
                  'os': {'platform': 'ubuntu', 'version': '22.04.3 LTS (Jammy Jellyfish)', 'family': 'debian', 'name': 'Ubuntu', 'kernel': '6.2.0-1016-azure', 'codename': 'jammy', 'type': 'linux'},
                  'id': '2d5470e779924f7b9040ceb830737783',
                  'containerized': False,
                  'ip': ['10.230.0.5', 'fe80::222:48ff:fe6c:c408', '172.17.0.1', 'fe80::42:80ff:fe7b:6d03', 'fe80::289a:44ff:fec8:656e'],
                  'name': 'backend-imageproxy01-vm'
              }
          },
          'sort': [1713415637885]
          }
```