FROM node:22-alpine
WORKDIR /app
COPY pesto-audit/package.json ./package.json
RUN npm install --omit=dev
COPY pesto-audit/ ./
ENV PORT=10000
EXPOSE 10000
CMD ["npm","start"]
