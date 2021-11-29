#!/bin/sh

# Comment out the Confluent configure script and substitute my own
sed -e '\/etc\/confluent\/docker\/configure/s/^/#/g' -i /etc/confluent/docker/run
sed -e '\/etc\/confluent\/docker\/ensure/s/^/#/g' -i /etc/confluent/docker/run

# Configure the environment using data from Azure
python config.py

# modify the launch script to use HTTP authentication libraries
sed -e '/exec /s/^/#/g' -i /etc/confluent/docker/launch
#echo "export KAFKAREST_OPTS=\"-Djava.security.auth.login.config=/etc/kafka-rest/rest-jaas.properties\" -DDEBUG=true -Dorg.eclipse.jetty.LEVEL=DEBUG -Djavax.net.debug=ssl,handshake,data " >> /etc/confluent/docker/launch
#echo "export KAFKAREST_OPTS=\"-Djava.security.auth.login.config=/etc/kafka-rest/rest-jaas.properties\"" >> /etc/confluent/docker/launch
echo 'exec "${COMPONENT}"-start /etc/"${COMPONENT}"/"${COMPONENT}".properties' >> /etc/confluent/docker/launch

# convert the downloaded CER file to JKS keystore
#openssl x509 -outform der -in https_certificate.pem -out https_certificate.der
#keytool -importcert -file https_certificate.der -alias localhost -noprompt -storepass password -keystore /etc/kafka-rest/kafka.restproxy.keystore.jks -storetype jks

openssl pkey -in https_certificate.pem -passin pass:password -out private.pem
openssl x509 -in https_certificate.pem -out public.pem
openssl pkcs12 -export -out /etc/kafka-rest/kafka.restproxy.keystore.p12 -inkey private.pem -in public.pem -password pass:password

# Run the REST proxy
/etc/confluent/docker/run
