# Benchmark data from the article "AutoPT: How Far Are We from End2End Automated Web Penetration Testing?"

This project is collected and compiled from the [Vulhub](https://github.com/vulhub/vulhub) project.

## Installation

Install Docker on Ubuntu 22.04:

```bash
# Install the latest version docker
curl -s https://get.docker.com/ | sh

# Run docker service
systemctl start docker
```

Note that as of April 2022, `docker compose` is merged into Docker as a subcommand as [Docker Compose V2](https://www.docker.com/blog/announcing-compose-v2-general-availability/), the Python version of `docker-compose` will be deprecated after June 2023. So Vulhub will no longer require the installation of additional `docker-compose`, and all documentation will be modified to use the `docker compose` instead.

The installation steps of Docker and Docker Compose for other operating systems might be slightly different, please refer to the [docker documentation](https://docs.docker.com/) for details.

## Usage
```bash
# Download project
wget https://github.com/vulhub/vulhub/archive/master.zip -O vulhub-master.zip
unzip vulhub-master.zip
cd vulhub-master

# Enter the directory of vulnerability/environment
cd flask/ssti

# Compile environment
docker compose build

# Run environment
docker compose up -d
```

There is a **README** document in each environment directory, please read this file for vulnerability/environment testing and usage.

After the test, delete the environment with the following command.
```bash
docker compose down -v
```
It is recommended to use a VPS of at least 1GB memory to build a vulnerability environment. The your-ip mentioned in the documentation refers to the IP address of your VPS. If you are using a virtual machine, it refers to your virtual machine IP, not the IP inside the docker container.

**All environments in this project are for testing purposes only and should not be used as a production environment!**

## Notice
1. To prevent permission errors, please ensure that the docker container has permission to access all files in the current directory.
2. This project does not support running on machines with non-x86 architecture such as ARM for now.