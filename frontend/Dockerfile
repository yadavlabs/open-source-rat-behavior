FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 4200
#CMD ["npx", "npm", "start", "serve", "--host", "0.0.0.0"]
CMD ["npm", "run", "start"]
#CMD ["npm", "run", "ng", "serve", "--host", "0.0.0.0"]