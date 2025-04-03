import json

a = {'x':"derzeit", 'c':123}

n = json.dumps(a)

z = json.loads(n)

print(z['x'])


