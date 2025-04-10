# ---- Stage 1: Build ----
# Use an official Node.js LTS version as a parent image.
# Alpine versions are smaller.
FROM node:20-alpine AS builder

# Set the working directory in the container
WORKDIR /app

# Copy package.json and package-lock.json (or yarn.lock)
COPY package*.json ./

# Install all dependencies (including devDependencies needed for build)
# Using npm ci is generally recommended for CI/CD environments as it uses the lock file
# and provides faster, more reliable builds.
RUN npm ci

# Copy the rest of the application source code
COPY . .

# Run the build script defined in package.json (compiles TS to JS)
RUN npm run build

# Remove development dependencies after build is complete
# This step is optional if you copy node_modules selectively later,
# but it ensures the node_modules copied in the next stage are clean.
# RUN npm prune --production

# ---- Stage 2: Production ----
# Use a slim Node.js image for the final stage
FROM node:20-alpine

# Set the working directory
WORKDIR /app

# Copy package.json and package-lock.json again to ensure consistency
# We'll use these to install *only* production dependencies
COPY package*.json ./

# Install only production dependencies
RUN npm ci --only=production

# Copy the built application code (dist folder) from the builder stage
COPY --from=builder /app/dist ./dist

# Copy production node_modules from the builder stage
# This is an alternative to running `npm ci --only=production` in this stage,
# especially if you ran `npm prune --production` in the builder stage.
# Choose *one* method for node_modules: either `npm ci --only=production` here,
# or uncomment the `npm prune` in builder and the COPY below.
# COPY --from=builder /app/node_modules ./node_modules

# The application listens on port 3000 by default
EXPOSE 3000

# Good practice: Run the application as a non-root user for security
# The node base images include a 'node' user
USER node

# Define the command to run the application
# This will execute `node dist/index.js`
CMD ["node", "dist/index.js"]