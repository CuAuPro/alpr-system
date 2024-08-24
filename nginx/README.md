# Nginx

## HTTPS Certificates

For development, you can generate self-signed certificates. For production, use certificates from a trusted Certificate Authority (CA).

Use OpenSSL to generate a self-signed certificate:

```bash
mkdir -p certs/https & cd certs/https
openssl req -nodes -new -x509 -keyout key.pem -out cert.pem -days 3650
```