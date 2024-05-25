# Stage 1: Build the frontend
FROM node:18-alpine AS client
WORKDIR /app
COPY ./frontend/package.json ./frontend/package-lock.json ./
RUN npm install
COPY ./frontend/ .
RUN npm run build

# Use a small Nginx image as a base
FROM nginx:alpine

RUN mkdir -p /usr/share/nginx/html
COPY --from=client /app/dist/frontend/browser /usr/share/nginx/html

# Copy Nginx configuration
COPY ./frontend/nginx.conf /etc/nginx/nginx.conf

COPY ./backend/certs/https /etc/nginx/certs

# Expose necessary ports
EXPOSE 443

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]