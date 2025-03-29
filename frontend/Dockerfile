# Stage 1: Build the Next.js app
FROM node:18 as builder

WORKDIR /app

# Install dependencies without using yarn.lock
COPY package.json ./
RUN yarn install --no-lockfile

# Copy source files and build the app
COPY . . 
RUN yarn build

# Stage 2: Run the built Next.js app
FROM node:18-alpine as runner

WORKDIR /app

# Copy only the built files from the builder stage
COPY --from=builder /app/.next .next
COPY --from=builder /app/node_modules node_modules
COPY --from=builder /app/package.json package.json

EXPOSE 3000

# Start Next.js
CMD ["yarn", "start"]
