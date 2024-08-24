# Stage 1: Build the frontend
FROM node:20-alpine AS client
WORKDIR /app
COPY ./package.json ./package-lock.json ./
RUN npm install
COPY . .
RUN npm run build

# Stage 2: Serve the frontend
FROM node:20-alpine
RUN npm install -g serve
WORKDIR /app
COPY --from=client /app/dist/frontend/browser /app
EXPOSE 4200
CMD ["serve", "-s", ".", "-l", "4200"]
