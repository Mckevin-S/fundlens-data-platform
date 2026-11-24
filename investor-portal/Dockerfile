FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM httpd:2.4-alpine
# Apache sert le build statique et relaie /portal vers le BFF (voir infra/compose/httpd.conf)
COPY --from=build /app/dist /usr/local/apache2/htdocs/
