# frontend/Dockerfile
FROM node:20-alpine

# Set the working directory to /app
WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install ALL dependencies (including Vite)
RUN npm install

# Copy the rest of the code
COPY . .

# Expose the Vite port
EXPOSE 5173

# Start the development server
CMD ["npm", "run", "dev", "--", "--host"]