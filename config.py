#!/usr/bin/env python3

# Configure the REST proxy using details from Azure Key Vault
# Simon Duff <sduff@confluent.io>
import sys, os, re

from azure.keyvault.secrets import SecretClient
from azure.keyvault.certificates import CertificateClient
from azure.identity import DefaultAzureCredential

# easy access to environment variables
def env(name,d=""):
    return os.environ[name] if name in os.environ else d

# Azure Key Vault Secrets
credential = DefaultAzureCredential(exclude_shared_token_cache_credential=True)
vault_url = env("VAULT_URI")
secret_client = SecretClient(vault_url=vault_url, credential=credential)
certificate_client = CertificateClient(vault_url=vault_url, credential=credential)

s = "localhost2"

# Get all secrets from key vault
try:
    secret_properties = secret_client.list_properties_of_secrets()

    for sp in secret_properties:
        print(sp.name)
        secret = secret_client.get_secret(sp.name)
        print("\t",secret)

except Exception as e:
    print (e)
    sys.exit(1)

# write certificate to filesystem
c = secret_client.get_secret(s)
with open('https_certificate.pem','w') as cert:
    cert.write(c.value)

bootstrap_server =  env("CCLOUD_BROKER_URL")
ccloud_key =        env("CCLOUD_KEY")
ccloud_secret =     env("CCLOUD_SECRET")
sr_url =            env("SR_URL")
sr_key =            env("SR_KEY")
sr_secret =         env("SR_SECRET")

# Template for kafka-rest.properties
template_kafka_rest = f"""
# Kafka
bootstrap.servers={bootstrap_server}
security.protocol=SASL_SSL
sasl.jaas.config=org.apache.kafka.common.security.plain.PlainLoginModule required username="{ccloud_key}" password="{ccloud_secret}";
ssl.endpoint.identification.algorithm=https
sasl.mechanism=PLAIN
client.bootstrap.servers={bootstrap_server}
client.security.protocol=SASL_SSL
client.sasl.jaas.config=org.apache.kafka.common.security.plain.PlainLoginModule required username="{ccloud_key}" password="{ccloud_secret}";
client.ssl.endpoint.identification.algorithm=https
client.sasl.mechanism=PLAIN

# Schema Registry specific settings
client.basic.auth.credentials.source=USER_INFO
client.schema.registry.basic.auth.user.info={sr_key}:{sr_secret}
schema.registry.url={sr_url}

# HTTP Basic Auth
#authentication.method=BASIC
#authentication.realm=KafkaRest
#authentication.roles=myrole
#confluent.rest.auth.propogate.method=JETTY_AUTH

# HTTPS
host.name=localhost
debug=true
listeners=https://0.0.0.0:8082
ssl.truststore.location=/etc/kafka-rest/kafka.restproxy.keystore.p12
ssl.truststore.password=password
ssl.keystore.location=/etc/kafka-rest/kafka.restproxy.keystore.p12
ssl.keystore.password=password
ssl.key.password=password
"""

with open("/etc/kafka-rest/kafka-rest.properties", "w") as f:
    f.write(template_kafka_rest)


template_logger = f"""
log4j.rootLogger=default('INFO'), stdout

log4j.appender.stdout=org.apache.log4j.ConsoleAppender
log4j.appender.stdout.layout=org.apache.log4j.PatternLayout
log4j.appender.stdout.layout.ConversionPattern=[%d] %p %m (%c)%n
"""

with open("/etc/kafka-rest/log4j.properties", "w") as f:
    f.write(template_logger)



# Write JAAS file
template_rest_jaas = """
KafkaRest {
  org.eclipse.jetty.jaas.spi.PropertyFileLoginModule required
  debug="true"
  file="/etc/kafka-rest/password.properties";
};
"""

with open("/etc/kafka-rest/rest-jaas.properties", "w") as f:
    f.write(template_rest_jaas)


# Write password file, using Azure data
template_password = f"""
svc_sduff_test:password,myrole
"""

with open("/etc/kafka-rest/password.properties", "w") as f:
    f.write(template_password)


print("REST Proxy configured!")
