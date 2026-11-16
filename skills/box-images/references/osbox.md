# osbox

`lqdflying/osbox` is the general network troubleshooting image and the base of `lqdflying/azurebox`. It has no Azure CLI, no PostgreSQL client, and no Azure protocol packages.

## Image

- Launch with tag `latest`.
- Debian 13 (trixie). 193 MiB compressed, 588 MB on disk.
- Python 3.13.5 with `pip`, `venv`, `requests` 2.32.3, plus `jq` 1.7.

## Tools in 5.0

| Category | Commands |
|----------|----------|
| Discovery and connectivity | `nmap`, `nc`, `socat`, `mtr`, `traceroute`, `tcptraceroute`, `httping`, `arping`, `ping` |
| DNS, web, TLS | `dig`, `nslookup`, `host`, `whois`, `curl`, `wget`, `openssl` |
| Packet capture and decode | `tcpdump`, `tshark`, `ngrep` |
| Throughput, link, sockets | `iperf3`, `ethtool`, `lsof`, `ipcalc`, `nload`, `iftop`, `ss`, `netstat` |
| Firewall, NAT, bridges | `iptables`, `nft`, `conntrack`, `brctl` |
| Routing and interfaces | `ip`, `ifconfig` |
| System diagnostics | `strace` |
| Legacy clients | `telnet`, `ftp` |
| Access and editing | `ssh`, `sshd`, `sudo`, `vim` |

## Launch

Docker, with SSH on loopback. Ready to paste as-is:

```bash
docker run -d --name osbox \
  -p 127.0.0.1:2222:22 \
  -v osbox-ssh:/etc/ssh \
  lqdflying/osbox:latest
docker exec -it osbox bash
```

Kubernetes. Ready to paste as-is:

```bash
kubectl run osbox --restart=Never --image=lqdflying/osbox:latest
kubectl exec -it osbox -- bash
```

Host-network diagnostics on a Docker host. This shell can read and change the host's network state. Ready to paste as-is:

```bash
docker run --rm -it --network host --cap-add NET_ADMIN --cap-add NET_RAW \
  --entrypoint /bin/bash lqdflying/osbox:latest
```

`tcpdump`, `tshark`, and `ngrep` work with Docker's default `NET_RAW` capability. Changes through `iptables`, `nft`, or `conntrack` need `NET_ADMIN`.

## Cleanup

```bash
docker rm -f osbox
kubectl delete pod osbox
```
