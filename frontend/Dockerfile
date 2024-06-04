# Stage 1: Build the frontend
FROM node:18-alpine AS client
WORKDIR /app
COPY ./package.json ./package-lock.json ./
RUN npm install
COPY . .
RUN npm run build

# Use a small Nginx image as a base
FROM nginx:alpine

RUN mkdir -p /usr/share/nginx/html
COPY --from=client /app/dist/frontend/browser /usr/share/nginx/html

# Copy Nginx configuration
COPY ./nginx.conf /etc/nginx/nginx.conf

# Expose necessary ports
EXPOSE 443

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]