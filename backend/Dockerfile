# Use a Node.js base image
FROM node:18-alpine

# Set the working directory in the container
WORKDIR /app/backend

# Copy package.json and package-lock.json to the container
COPY package*.json ./

# Install npm dependencies
RUN npm install

# Copy the rest of the application code to the container
COPY ./ ./

RUN npm run build

# Expose the port the app runs on
EXPOSE 443

# Start the application
CMD ["npm", "run", "start"]
