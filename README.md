mongo:5.0docker run -d --name db -p 27017:27017 -v mongo_data:/data/db mongo:5.0 

docker run -d --name db -p 27017:27017 -v mongo_data:/data/db mongo:5.0 

docker run -d --name rocketchat -p 80:3000 --link db --env ROOT_URL=http://localhost --env MONGO_URL=mongodb://db:27017/rocketchat --env MONGO_OPLOG_URL=mongodb://db:27017/local rocket.chat