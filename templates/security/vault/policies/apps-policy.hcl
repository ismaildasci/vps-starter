# Policy for application secrets
# Allows read-only access to secrets for applications

path "secret/data/telegram/*" {
  capabilities = ["read"]
}

path "secret/data/grafana/*" {
  capabilities = ["read"]
}

path "secret/data/alertmanager/*" {
  capabilities = ["read"]
}

path "secret/data/apps/*" {
  capabilities = ["read"]
}

# Add more paths as needed for your applications
# path "secret/data/myapp/*" {
#   capabilities = ["read"]
# }
