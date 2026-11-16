---
name: box-images
description: >-
  Bring up a disposable test container or pod from the public toolbox images
  lqdflying/osbox (general network troubleshooting) and lqdflying/azurebox
  (Azure service integration, built on osbox). Use when a task needs a test
  environment to check connectivity, DNS, TLS, packet flow, or firewall
  behavior, or to try Azure identity, RBAC, Blob Storage, Key Vault, Event
  Hubs, or PostgreSQL from inside a network, including as an AKS pod with
  workload identity. Use instead of building a test image or installing tools
  on a node. Done when the container or pod runs the latest tag, the
  requested check ran inside it and its outcome is reported,
  port 22 has no Service, Ingress, or host port and is published only on
  loopback in Docker, and no token or secret value is printed.
---

# Box Images

Public Docker Hub images that give a ready shell with test tools. Use one instead of building a test image or installing tools on a node.

## Load First

Read the reference for the image you pick:

- `references/osbox.md` for `lqdflying/osbox`
- `references/azurebox.md` for `lqdflying/azurebox`

## Pick the image

| Need | Image | Reference |
|------|-------|-----------|
| Network checks with no cloud tooling: reachability, DNS, TLS, packet capture, throughput, firewall and NAT state | `lqdflying/osbox` | `references/osbox.md` |
| Azure service integration: identity, RBAC, Blob Storage, Key Vault, Event Hubs, PostgreSQL, Azure Resource Manager. Includes every osbox tool | `lqdflying/azurebox` | `references/azurebox.md` |

Pick `osbox` unless the check needs the Azure CLI, a PostgreSQL client, or an Entra token.

## Shared behavior

`azurebox` is built `FROM lqdflying/osbox`, so both images behave the same way here:

- linux/amd64 only. They do not run on arm64 nodes.
- Debian 13 with Python 3.13, `pip`, `requests`, and `jq`. `pip install <package>` works system-wide.
- No `kubectl` and no `git`.
- The entrypoint `/start.sh` sets a random password for `root` and `liuqd`, prints it to the container log, writes it to `/tmp/password.txt`, and runs `sshd` on port 22. The container keeps running until you remove it.
- The container must run as root with a writable root filesystem. A pod policy that enforces `runAsNonRoot` or a read-only root filesystem blocks it.
- `/etc/ssh` is a declared volume and holds the host keys from the image. An empty volume mounted there, such as a Kubernetes `emptyDir`, leaves `sshd` without host keys.
- An SSH session does not inherit the container environment. Use `docker exec` or `kubectl exec` when the check reads environment variables.

## Workflow

1. Pick the image from the table and read its reference.
2. Read the image overview when you need its full manifest or code samples. Ready to paste after you replace `<image>` with `osbox` or `azurebox`:

   ```bash
   curl -fsS "https://hub.docker.com/v2/repositories/lqdflying/<image>/" | jq -r .full_description
   ```

3. Start the container or pod with the launch commands in the reference. Use `lqdflying/<image>:latest`.
4. Open a shell with `docker exec -it <name> bash` or `kubectl exec -it <pod> -- bash` and run the check.
5. Report the command and its outcome.
6. Remove the container or pod, or tell the user it is still running.

## Limits

Both images are intentionally unhardened: root SSH login, password authentication, passwordless sudo for `liuqd`, and host keys that ship in a public image. Anyone who can read the container log can log in as root.

- Use them only as disposable containers on a trusted network.
- Publish port 22 on loopback only (`-p 127.0.0.1:2222:22`). In Kubernetes use `kubectl port-forward`. Never create a Service, an Ingress, or a host port for it.
- In Kubernetes the pod IP accepts TCP 22 from every pod and node in the cluster unless a network policy denies it. On a flat-network AKS cluster (Azure CNI Pod Subnet or Node Subnet) it also accepts it from the virtual network and connected networks. Run the pod only where that is acceptable, and delete it when the check is done.
- Do not print, log, or store access tokens, secret values, or the generated password.

## Delivery checklist

- The image came from the table above, not a new build.
- The launch used the `latest` tag.
- The check ran inside the container or pod, and the reply gives the command and its outcome.
- Port 22 is published on loopback only in Docker. In Kubernetes it has no Service, Ingress, or host port, and the reply states that the pod IP accepts TCP 22 from the cluster network.
- The reply contains no token, secret value, or password.
- The container or pod is removed, or the reply says it is still running.
