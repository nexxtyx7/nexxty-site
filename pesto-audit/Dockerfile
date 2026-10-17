FROM node:22-alpine
WORKDIR /app
COPY package.json ./
RUN npm install --omit=dev
COPY . .
ENV PORT=10000
EXPOSE 10000
CMD ["npm","start"]
