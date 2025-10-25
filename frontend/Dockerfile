# ---- builder ----
FROM node:20-alpine AS builder
WORKDIR /usr/src/app

# copy manifests first (add lock if you have it)
COPY package.json ./
# COPY package-lock.json ./

# install WITH dev deps so postcss/autoprefixer/tailwind are available at build
RUN npm install --include=dev

# copy the rest
COPY . .

# sanity checks so we know the build context has the right files/lines
RUN echo "=== sanity ===" \
 && ls -la src/app/styles || true \
 && grep -n 'import "./styles/globals.css"' src/app/layout.tsx

# build Next.js
RUN npm run build

# ---- runner ----
FROM node:20-alpine AS runner
WORKDIR /usr/src/app
ENV NODE_ENV=production

# copy build output and minimal runtime files
COPY --from=builder /usr/src/app/.next ./.next
COPY --from=builder /usr/src/app/public ./public
COPY --from=builder /usr/src/app/package.json ./package.json

# prod deps only
RUN npm install --omit=dev

EXPOSE 3000
CMD ["npm","run","start","--","-p","3000"]
