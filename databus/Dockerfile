#
# Dockerfile for building MQTTS
#

# Build the MQTTS using phusion base image
FROM phusion/baseimage:jammy-1.0.1

# Installing mosquitto packages and certbot
RUN apt-add-repository ppa:mosquitto-dev/mosquitto-ppa
RUN apt-get update && apt-get install -y \
	certbot \ 
	mosquitto \ 
	mosquitto-clients

# Start the MQTTS daemon during container startup
RUN mkdir /etc/service/mosquitto
COPY mosquitto.sh /etc/service/mosquitto/run
RUN chmod +x /etc/service/mosquitto/run

# end of file
