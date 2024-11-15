## Cisco DC Lab

### Introduction

This lab shows us an example of DC networks. During the lab you will:

- Deploy the whole configuration on ToRs and spines
- Change the role of one of the ToRs to an unknown role and deploy configuration on the ToR and every spine
- Set maintenance tag on one of the spines and deploy configuration on the spine

Author:

- [Grigorii Solovev](https://github.com/gs1571)

### Objectives

- Understand main principles of writing Annet generators

### Preparation

Before you start, please put Cisco IOS image `c7200-jk9s-mz.124-13a.bin` into `lab/vm_images` directory.
The image is subject to a license agreement, so it cannot be distributed in the repository.

### Topology

![lab-topology](./images/topology.png)

Naming:

- Spine - `spine-<pod>-<plane>`
- ToR - `tor-<pod>-<num>`
- Router ID spine - `1.2.<pod>.<plane>`
- Router ID ToR - `1.1.<pod>.<num>`
- ASNUM spine - `6520<pod>`
- ASNUM ToR - `6510<pod><num>`

### Generators

In this lab, generators are organized within the `./src/lab_generators` directory. The lab utilizes the following generators:

- Hostname
- Interface IP addresses, descriptions and shutdown state
- Route map
- BGP process

Important notice, BGP attributes are generated by mesh model. Mesh models allow assigning attributes to devices, following the connections between them.

#### Hostname

The default configuration has basic names like `tor` or `spine`. The generator sets these names to hostnames taken from Netbox.

[src](./src/lab_generators/hostname.py)

#### Interface descriptions

Following the connections in Netbox, the descriptions on the interfaces are created as `remote_hostname@remote_port`.

[src](./src/lab_generators/description.py)

#### Interface shutdown

The generator sets `no shutdown` to every interface on the device.

[src](./src/lab_generators/description.py)

#### Interface IP addresses

The lab has two kinds of IP addresses:

1. IP addresses known from Netbox
2. IP addresses on links between ToRs and spines which are generated by the mesh model

The generator collects the two kinds of addresses and assigns them to the interfaces.

- [generator src](./src/lab_generators/ip_address.py)
- [mesh spine src](./src/lab_generators/mesh_views/spine.py)
- [mesh tor src](./src/lab_generators/mesh_views/tor.py)

#### Route map

For BGP, neighbors and `redistribute connected` route-maps are needed, which should be generated before BGP process. An interesting thing to do is to apply `maintenance` tag on a spine, and then drain traffic there. The role is also important for the generator.

[src](./src/lab_generators/rpl.py)

#### BGP process

BGP neighbors also depend on the connections in Netbox, they are generated only if a connection is present. This is supported by the mesh models.

- [generator src](./src/lab_generators/bgp.py)
- [mesh spine src](./src/lab_generators/mesh_views/spine.py)
- [mesh tor src](./src/lab_generators/mesh_views/tor.py)

### Lab Guide

**Step 1.**

If it was not done in one of the previous labs, build Netbox and Annet docker images:

```bash
cd annetutils/contribs/labs
make build
```

**Step 2.**

NOTE: Do not forget to put Cisco IOS image `c7200-jk9s-mz.124-13a.bin` into `../vm_images` directory.

Start the lab:

```bash
make lab02
```

**Step 3.**

Go to the Annet container:

```bash
docker exec -u root -t -i annet /bin/bash
```

Enable SSH on Cisco routers by executing the script:

```bash
for ip in 0 1 2 3 4; do netsshsetup -a 172.20.0.10$ip -b ios -l annet -p annet -P telnet -v cisco --ipdomain nh.com; done
```

**Step 4.**

Go to the Annet container:

```bash
docker exec -u root -t -i annet /bin/bash
```

Generate configuration for spine-1-1, spine-1-2, tor-1-1, tor-1-2, tor-1-3:

`annet gen spine-1-1.nh.com spine-1-2.nh.com tor-1-1.nh.com tor-1-2.nh.com tor-1-3.nh.com`

Look at diff:

`annet diff spine-1-1.nh.com spine-1-2.nh.com tor-1-1.nh.com tor-1-2.nh.com tor-1-3.nh.com`

Deploy it:

`annet deploy spine-1-1.nh.com spine-1-2.nh.com tor-1-1.nh.com tor-1-2.nh.com tor-1-3.nh.com`

**Step 5.**

Assign "Unknown" role to one of the ToRs and deploy configuration on the ToR and every spine.

Go to the [Netbox](http://localhost:8000/), use annet:annet as login:password. Assign tor-1-1.nh.com role "Unknown".

Look at diff:

`annet diff spine-1-1.nh.com spine-1-2.nh.com tor-1-1.nh.com tor-1-2.nh.com tor-1-3.nh.com`

Deploy it:

`annet deploy spine-1-1.nh.com spine-1-2.nh.com tor-1-1.nh.com tor-1-2.nh.com tor-1-3.nh.com`

Restore the role and repeat the actions.

**Step 6.**

Break a connection and check what happens.

Go to [Netbox](http://localhost:8000/), use annet:annet as login:password. Delete the connection between tor-1-1.nh.com and spine-1-1.nh.com.

Look at diff:

`annet diff spine-1-1.nh.com spine-1-2.nh.com tor-1-1.nh.com tor-1-2.nh.com tor-1-3.nh.com`

Deploy it:

`annet deploy spine-1-1.nh.com spine-1-2.nh.com tor-1-1.nh.com tor-1-2.nh.com tor-1-3.nh.com`

Restore the connection and repeat the actions.

**Step 7.**

Drain traffic from one of the spines.

Go to [Netbox](http://localhost:8000/), use annet:annet as login:password. Assign spine-1-1.nh.com tag "maintenance".

Look at diff:

`annet diff spine-1-1.nh.com spine-1-2.nh.com tor-1-1.nh.com tor-1-2.nh.com tor-1-3.nh.com`

Deploy it:

`annet deploy spine-1-1.nh.com spine-1-2.nh.com tor-1-1.nh.com tor-1-2.nh.com tor-1-3.nh.com`

Remove the tag and repeat the actions.

**Step 8.**

After finishing the lab, stop it:

```bash
make services_stop
```