# FROM node:18-alpine
#
# WORKDIR /app
#
# COPY package*.json ./
# RUN npm install
#
# COPY . .
#
# EXPOSE 3000
# EXPOSE 443
#
# CMD ["npm", "start", "--", "--host", "0.0.0.0", "--port", "443"]

FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build  # Собираем статические файлы


FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf