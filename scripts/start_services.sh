docker-compose up -d mysql
sleep 15
docker-compose up -d chatgpt-wrapper
sleep 15
docker-compose up -d nginx
