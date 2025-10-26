# -------- 1. Builder stage: install deps and build Next.js --------
FROM node:20-alpine AS builder

# create a working directory inside the container
WORKDIR /usr/src/app

# copy only the package metadata first for better Docker layer caching
# (if you have package-lock.json, it'll get copied too; if you don't, it's fine)
COPY package.json package-lock.json* ./

# install dependencies (including dev deps so Next.js can build)
# ALSO install chart.js + react-chartjs-2 to satisfy ChartSentiment.tsx
RUN npm install --include=dev \
    && npm install react-chartjs-2 chart.js

# now copy the rest of the frontend source code into the image
COPY . .

# build the production Next.js app
RUN npm run build


# -------- 2. Runtime stage: lightweight image just to run `next start` --------
FROM node:20-alpine AS runner
WORKDIR /usr/src/app

# Copy only what's needed to run the built app in production
# - the compiled .next output
# - public assets
# - package.json to define runtime scripts
# - node_modules (prod + whatever we installed above)
# - next.config.mjs for runtime config
COPY --from=builder /usr/src/app/.next ./.next
COPY --from=builder /usr/src/app/public ./public
COPY --from=builder /usr/src/app/package.json ./package.json
COPY --from=builder /usr/src/app/next.config.mjs ./next.config.mjs
COPY --from=builder /usr/src/app/node_modules ./node_modules

# set required env
ENV PORT=3000
ENV NODE_ENV=production

EXPOSE 3000

# run the Next.js production server
CMD ["npm", "run", "start"]
