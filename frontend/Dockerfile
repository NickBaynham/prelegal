FROM node:22-bookworm-slim AS builder

WORKDIR /app

# NEXT_PUBLIC_* values are inlined at build time, so they must be passed as
# build args. Default matches local docker-compose; override in CI/prod.
ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL} \
    PUPPETEER_SKIP_DOWNLOAD=1

COPY package.json package-lock.json* ./
RUN npm ci

COPY tsconfig.json next.config.ts postcss.config.mjs ./
COPY app ./app
COPY components ./components
COPY lib ./lib

RUN npm run build

FROM node:22-bookworm-slim AS runtime

ENV NODE_ENV=production \
    PUPPETEER_SKIP_DOWNLOAD=1 \
    PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium \
    NEXT_TELEMETRY_DISABLED=1

# Chromium and the minimal font/library set Puppeteer needs to render PDFs.
RUN apt-get update && apt-get install -y --no-install-recommends \
        chromium \
        fonts-liberation \
        fonts-dejavu-core \
        ca-certificates \
        dumb-init \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/node_modules/puppeteer ./node_modules/puppeteer

EXPOSE 3000

ENTRYPOINT ["dumb-init", "--"]
CMD ["node", "server.js"]
