# EKUCourseMonitor
Web app for monitoring course availability at Eastern Kentucky University

# Installation Instructions Using Docker Compose

First, clone the repo.
```bash
git clone https://github.com/KYDronePilot/EKUCourseMonitor.git
```

Edit the `<host.domain>` and `<user@example.com>` placeholders to your server's FQDN and your email for Certbot,
respectively in `certbot/Dockerfile`.
```dockerfile
...
# FQDN of the server.
ENV FQDN <host.domain>

# Email used with certbot.
ENV EMAIL <user@example.com>
...
```

Make a copy of the nginx config.
```bash
cd config/nginx/
cp course_monitor.conf.base course_monitor.conf
```

Edit the deployment-specific fields in the nginx config.
```
...
server {
    listen 443 ssl;
    server_name <host.domain>;
...

...
server {
    if ($host = <host.domain>) {
        return 301 https://$host$request_uri;
    }

    listen 80;
    server_name <host.domain>
    return 404;
}
...
```

Make a copy of the example Django env file.
```bash
cd EKUCourseMonitorWebpage
cp example.env .env
```

Edit it to fit your needs.
```
SECRET_KEY=<secret-key>
DEBUG=<True/False>
ALLOWED_HOSTS=*
DATABASE_URL=postgres://postgres@db:5432/postgres
STATIC_ROOT=/static
GMAIL_USERNAME=<alert-sending-email-addr>
GMAIL_PASSWORD=<password>
```

Go to certbot, create an image and container, and run the cert renewal script.
```bash
cd certbot
./image_build.sh
./renew.sh
```

Set timezone on the host machine.
```bash
echo "America/Kentucky/Louisville" > /etc/timezone
unlink /etc/localtime
dpkg-reconfigure -f noninteractive tzdata
```

Add a cron job to try renewing the cert every week.
```
0 4 * * 0 /bin/bash <absolute path>/renew.sh
```

Compose the project (run twice first time).
```bash
docker-compose up
```

Everything should now be working!
