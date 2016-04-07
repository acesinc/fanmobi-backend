fanmobi-backend
=========================
Backend RESTful API for FanMobi

## Getting Started
Ansible can be used to provision a new Ubuntu 14.04 box with the Fanmobi
backend REST service. This has been tested with both Vagrant and AWS
boxes. In either case, the first step is to create a public/private keypair
and upload the public key to GitHub so that Ansible can clone the
private GitHub repo

### Configure GitHub Keypair
This GitHub repo is private, so in order to run these Ansible scripts (that
clone the repo), you'll need to do the following:

1. Create a public/private ssh keypair using `ssh-keygen -t rsa -b 4096 -C "your_email@example.com"`.
DO NOT set a passprhase on the private key

2. Upload the public key to GitHub, as a "Deploy Key" in the `fanmobi-backend`
repository. Leave it as read-only.

3. Move your private key to `deploy/roles/common/files`

4. Change the value of `github_private_key` in `group_vars/all/all.yml` to the
name of your private key

*NOTE*: Do not put these keys in the git repository

### Deploying locally with Vagrant
**NOTE:** Due to a current issue with Vagrant 1.8.1 and Ubuntu 14.04, the built-in
Ansible-Vagrant integration is not working. Until that is resolved, you will
need to install Ansible yourself on your host machine and use it to provision
the Vagrant box manually.

You will also need to install VirtualBox and Vagrant

Assuming you've installed Ansible, VirtualBox, and Vagrant, and went through
the public/private keypair steps above:

1. set `reset_database: true` in `deploy/roles/fanmobi_backend/vars/main.yml`
2. do a `vagrant up` in the `deploy/` directory and wait for it to finish
3. `ansible-playbook site.yml -i hosts_vagrant -u vagrant -k` in `deploy/`.
The SSH password is `vagrant`. If you get a "host unreachable" error, look
in `~/.ssh/known_hosts` for an entry for `192.168.33.10` and remove it

The API should now be available from your host at `http://localhost:10000/docs`,
or `http://192.168.33.10:10000/docs`

### Deploying to AWS
First, launch an EC2 instance of type Ubuntu Server 14.04 LTS (HVM). When
selecting the security group, be sure to choose a group that allows incomming
HTTP traffic on port 10000

Verify that the machine is up and running: `ssh ubuntu@<public-ip> -i </path/to/aws/private/key.pem>` (this assumes you have already created a public/private keypair
for use with AWS). If this succeeds, just quit the ssh session.

Edit `deploy/hosts_aws` and set all ip addresses to the public ip address
of your ec2 instance

run: `ansible-playbook site.yml -i hosts_aws -u ubuntu --private-key </path/to/aws/private/key.pem>`
**NOTE:** use username `bitnami` instead of `ubuntu` on our current AWS box

The API should now be available publicly at `http://<aws-public-ip-or-dns>:10000/docs`

**NOTE:** Hit the `/api/login` link first - most endpoints require authentication.

You can use username (`anonymous_id`): bob (user), alice (user), counting_crows (artist),
or admin (admin)

### Redeploying code to AWS
To redeploy new code updates to an AWS box, you can simply run through the
process above after committing the changes to `master` and pushing. If you
haven't added any new dependencies and just need to update the code, you
can speed things up by running the `fanmobi_deploy.yml` playbook instead of
`site.yml`

## API Notes
Most of the documentation for the API should be accessed via Swagger. Below are
some high level descriptions of the various endpoints that should make
navigating the Swagger docs a little easier

General notes:
* PATCH requests are not implemented - don't try and use these
* PUT requests will update an entire record - if data is not provided, it will
    be treated as null
* Unless a user is an ADMIN, they only have access to their own data

### Login/Logout
All requests (other than these) must be authenticated. Session-based
authentication is used to keep track of the current user. The login endpoint
will create the user if they don't currently exist

####Useful endpoints
Method | Endpoint | Description
------ | -------- | -----
POST | `/api/login/` | login
POST | `/api/logout/` | logout

Permissions: open
### User
This is a lower-level thing used by default in Django - don't use this
endpoint directly

Permissions: ADMIN access only
### Group
A Group is a Role, and a user can belong to one or more groups. Currently, we
are using three groups: FAN, ARTIST, and ADMIN. There shouldn't be a need to
change anything here, but these three groups must be created in the database

Permissions: ADMIN access only
### Genre
Names of music genres. Artists have zero or more music genres associated with
them. **TBD:** Need to decide whether these genres are pre-populated and thus
read-only by non-ADMINs, or if artists should be able to create their own
genres

#### Useful endpoints
Method | Endpoint | Description
------ | -------- | -----
GET | `/api/genre/` | Get all genres

Permissions: ADMIN has full access, authenticated users have read-only

### Image
Images for use with avatars. Images are stored on disk (not in the database).
All Profiles can have an associated avatar (so they are not limited to artists)

Method | Endpoint | Description
------ | -------- | -----
GET | `/api/image/` | Get all images
POST | `/api/image/` | Upload an image (don't use Swagger to test this)
GET | `/api/image/<id>` | Get an image

Permissions: Authenticated has full access

### Profile
Every user of Fanmobi has a Profile. At a minimum, a Profile has an associated
user with a username and belongs to at least one Group (FAN by default). Trying
to access a user profile other than your own will result in a 403 (unless you
are an ADMIN). Once created, **usernames cannot currently be changed**

Profiles are created automatically when a new user tries to login. Note that
the POST endpoint to create a new user is not implemented yet

#### Useful Endpoints
Method | Endpoint | Usage
------ | -------- | -----
GET  | `/api/profile/` | returns all Profiles - ADMIN use only
GET  | `/api/profile/<id>/` | returns a user's profile
PUT  | `/api/profile/<id>/` | update a user's profile (cannot update avatar from Swagger)
GET | `/api/profile/<id>/message/` | returns all unread messages for a user
DELETE | `/api/profile/<profile_id>/message/<message_id>/` | mark a message as read
GET | `/api/profile/<profile_id>/connected/` | get artist connections
PUT | `/api/profile/<profile_id>/connected/<artist_id>/` | connect to an artist
DELETE | `/api/profile/<profile_id>/connected/<artist_id>/` | disconnect from an artist

### Artist
In addition to a Profile, artists have an ArtistProfile containing additional
information. Artists can also create messages for their followers and
update show information

#### Useful Endpoints
Method | Endpoint | Usage
------ | -------- | -----
POST | `/api/artist/` | create a new artist (for an existing user)
GET  | `/api/artist/` | returns all Artist profiles (open to any authenticated user)
GET  | `/api/artist/<id>/` | return information for a single artist
PUT  | `/api/artist/<id>/` | update artist information (does not work from Swagger)
GET  | `/api/artist/<id>/show/` | get all shows for an artist
POST  | `/api/artist/<id>/show/` | create a new show
PUT  | `/api/artist/<id>/show/<show_id>/` | update an existing show
DELETE  | `/api/artist/<id>/show/<show_id>/` | delete an existing show
GET  | `/api/artist/<id>/connected/` | get all users connected to this artist
GET  | `/api/artist/<id>/message/` | get all messages from this artist
POST  | `/api/artist/<id>/message/` | create a message from this artist
DELETE  | `/api/artist/<id>/message/<message_id>/` | delete this message
GET  | `/api/artists-in-radius/` | get artists in radius (km) of coordinates (latitude and longitude in decimal degrees)


Like other users, artists are created when a new user tries to login (and specifies
that they are an artist).

## Configuration Details
Logs:
* application: `/usr/local/fanmobi/fanmobi.log`
* gunicorn: `/var/log/upstart/gunicorn.log`
* nginx: `/var/log/nginx/error.log`

Notes:
* User uploaded images (avatars) are stored in `/usr/local/fanmobi/fanmobi_media`
* The SQLite database is located at `/usr/local/fanmobi/db.sqlite3`
* Static files (for Swagger docs) are served from `/usr/local/fanmobi/frontend/django_static`
* Restart nginx: `sudo service nginx restart`
* Restart gunicorn: `sudo service gunicorn restart`
