Deployment
===============
This directory contains a Vagrantfile and Ansible resources that can be
used to deploy the Fanmobi backend.

## GitHub Private Key
This GitHub repo is private, so in order to run these Ansible scripts (that
clone the repo), you'll need to do the following:

1. Create a public/private ssh keypair using `ssh-keygen -t rsa -b 4096 -C "your_email@example.com"`.
DO NOT set a passprhase on the private key!

2. Upload the public key to GitHub, as a "Deploy Key" in the `fanmobi-backend`
repository. Leave it as read-only.

3. Move your private key to `roles/common/files`

4. Change the value of `github_private_key` in `group_vars/all/all.yml` to the
name of your private key
