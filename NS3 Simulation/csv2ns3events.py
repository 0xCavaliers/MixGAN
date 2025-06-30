import csv
import random

NORMAL_NODE_RANGE = (0, 799)
ATTACK_NODE_RANGE = (800, 999)
AP_NODE = 1000

def pick_node(node_range):
    return random.randint(*node_range)

def get_port(service):
    if service == 'http':
        return 80
    elif service == 'ftp':
        return 21
    elif service == 'smtp':
        return 25
    elif service == 'domain_u':
        return 53
    else:
        return 9999 # default port

with open('iot-test.csv') as f, open('ns3_events_full.txt', 'w', newline='') as out:
    reader = csv.DictReader(f)
    sim_fields = ['src', 'dst', 'start', 'duration', 'size', 'proto', 'port']
    all_fields = sim_fields + reader.fieldnames
    writer = csv.DictWriter(out, fieldnames=all_fields)
    writer.writeheader()
    for row in reader:
        proto = row['Protocol Type'].lower()
        if proto not in ['udp', 'tcp', 'icmp']:
            continue
        if row['Class'] == 'normal':
            src = pick_node(NORMAL_NODE_RANGE)
        else:
            src = pick_node(ATTACK_NODE_RANGE)
        dst = AP_NODE
        start = 1 # change as you like
        duration = int(row['Duration']) if row['Duration'] else 1
        size = int(row['Src Bytes']) if row['Src Bytes'] else 64
        port = get_port(row['Service'])
        event = {
            'src': src,
            'dst': dst,
            'start': start,
            'duration': duration,
            'size': size,
            'proto': proto,
            'port': port
        }
        event.update(row)
        writer.writerow(event) 