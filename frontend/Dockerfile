# Stage 1: Build the Next.js app
FROM node:18 as builder

WORKDIR /app

# Copy package.json and install dependencies
COPY package.json ./
RUN yarn install --no-lockfile

# Copy source files and build the app
COPY . .
RUN yarn build

# Stage 2: Run the built Next.js app
FROM node:18-alpine as runner

WORKDIR /app

# Copy built files and .env from builder stage
COPY --from=builder /app/.next .next
COPY --from=builder /app/node_modules node_modules
COPY --from=builder /app/package.json package.json
COPY --from=builder /app/.env .env

EXPOSE 3000

# Start Next.js
CMD ["yarn", "start"]