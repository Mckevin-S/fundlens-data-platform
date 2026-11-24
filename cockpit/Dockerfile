FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npx ng build --configuration production

FROM httpd:2.4-alpine
COPY docker/httpd.conf /usr/local/apache2/conf/httpd.conf
COPY --from=build /app/dist/cockpit/browser /usr/local/apache2/htdocs/
