# azurebox

`lqdflying/azurebox` adds Azure tooling to `lqdflying/osbox`. It reaches Azure services over their public protocols and carries no `azure-*` SDK.

## Image

- Launch with tag `latest`.
- Built `FROM lqdflying/osbox:5.0`, so every tool in `osbox.md` is present. 330 MiB compressed, 1.25 GB on disk.
- Added in 1.1: Azure CLI 2.92.0, PostgreSQL client 17.12 (`psql`, `pg_dump`, `pg_restore`, `pg_isready`, `createdb`, `dropdb`), and the Python packages `psycopg` 3.2.6, `qpid-proton` 0.37.0 (`import proton`), `PyJWT` 2.10.1, `cryptography` 43.0.0.
- Not in the image: `confluent-kafka`, and any `azure-*` or `msal` package in system Python. Install one with `pip install <package>` when a test needs it.

## Launch in AKS

Prerequisites: the cluster has the OIDC issuer and workload identity enabled, and the managed identity or app registration has a federated credential with subject `system:serviceaccount:<namespace>:azurebox`.

Template. Replace `<managed-identity-client-id>`, set the namespace, and keep only the `env` entries the test uses.

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: azurebox
  namespace: default
  annotations:
    azure.workload.identity/client-id: "<managed-identity-client-id>"
---
apiVersion: v1
kind: Pod
metadata:
  name: azurebox
  namespace: default
  labels:
    azure.workload.identity/use: "true"
spec:
  serviceAccountName: azurebox
  restartPolicy: Never
  containers:
    - name: azurebox
      image: lqdflying/azurebox:latest
      env:
        - name: AZURE_STORAGE_ACCOUNT
          value: "<storage-account>"
        - name: AZURE_KEYVAULT_URL
          value: "https://<vault-name>.vault.azure.net/"
        - name: AZURE_EVENTHUB_FQDN
          value: "<namespace>.servicebus.windows.net"
        - name: AZURE_EVENTHUB_NAME
          value: "<event-hub>"
        - name: AZURE_PG_HOST
          value: "<server>.postgres.database.azure.com"
        - name: AZURE_PG_DATABASE
          value: "postgres"
        - name: AZURE_PG_USER
          value: "<entra-principal-name>"
```

The workload identity webhook injects `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_AUTHORITY_HOST`, and `AZURE_FEDERATED_TOKEN_FILE`. Do not set them in the manifest. The manifest has no Service on purpose.

```bash
kubectl apply -f azurebox.yaml
kubectl exec -it azurebox -- bash
kubectl delete -f azurebox.yaml
```

Use `kubectl exec` for identity work. An SSH session does not carry the workload identity variables.

## Launch in Docker

Ready to paste as-is:

```bash
docker run -d --name azurebox \
  -p 127.0.0.1:2222:22 \
  -v azurebox-ssh:/etc/ssh \
  lqdflying/azurebox:latest
docker exec -it azurebox bash
docker rm -f azurebox
```

## Tokens

Get an Entra token with plain OAuth2 through `requests`, or log in with the Azure CLI. The image overview holds a `get_token` helper that tries the workload identity federated token, then a client secret, then the Instance Metadata Service.

| Target | Scope |
|--------|-------|
| Azure Resource Manager | `https://management.azure.com/.default` |
| Blob Storage | `https://storage.azure.com/.default` |
| Key Vault | `https://vault.azure.net/.default` |
| Event Hubs | `https://eventhubs.azure.net/.default` |
| PostgreSQL | `https://ossrdbms-aad.database.windows.net/.default` |

Azure CLI login with workload identity. Ready to paste as-is inside the pod:

```bash
az login --service-principal \
  --username "$AZURE_CLIENT_ID" \
  --tenant "$AZURE_TENANT_ID" \
  --federated-token "$(cat "$AZURE_FEDERATED_TOKEN_FILE")"
```

`az login --identity` uses the Instance Metadata Service, which is a different path from workload identity.

For PostgreSQL the token is the password and TLS is required (`sslmode=require`). `az account get-access-token --resource-type oss-rdbms --query accessToken -o tsv` returns that token. The user name must equal the database role of the Entra principal.

## Service samples

The image overview holds the code for Blob Storage REST, Key Vault REST, Event Hubs REST send, the Event Hubs AMQP token exchange, and PostgreSQL with `psycopg`. Read it with the overview command in `SKILL.md` before you write a test script.

Check these two points in a sample before you use it. Both come from Microsoft Learn and are not confirmed against a live resource:

- `get_token`, Instance Metadata Service branch: if the sample appends `/` to every resource, remove it for Key Vault, Event Hubs, and PostgreSQL. Key Vault requires exactly `https://vault.azure.net`, and a mismatch returns 400 or 401. `https://storage.azure.com/` and `https://management.azure.com/` keep the slash. The workload identity and client secret branches need no change.
- `eventhub_send`: if the sample passes `json=event`, the request carries `Content-Type: application/json`. The Event Hubs REST reference specifies `application/atom+xml;type=entry;charset=utf-8`. Set that header when the send returns an error.

## Troubleshooting

| Symptom | Check |
|---------|-------|
| `AZURE_*` variables missing in the pod | The pod label `azure.workload.identity/use: "true"` and the service account annotation |
| 401 | Token scope, token expiry, and the federated credential subject. Decode `aud` and `exp` without printing the token |
| 403 `AuthorizationPermissionMismatch` | The data-plane role at that scope: Storage Blob Data Reader or Contributor, Key Vault Secrets User, Azure Event Hubs Data Sender or Receiver |
| Key Vault list returns 403 while a get works | Not the normal result of Key Vault Secrets User. The role allows both get (`getSecret`) and list (`readMetadata`). Check the scope of the role assignment, whether a different role is assigned, and whether the vault uses access policies instead of Azure RBAC |
| PostgreSQL `28P01` | `AZURE_PG_USER` does not match the database role name, or the server has no Entra admin |
| Variables present with `kubectl exec`, absent over SSH | Expected. Use `kubectl exec` |
