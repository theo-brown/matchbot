- On pip:
    1. Generate key pair with `ssh-keygen`
    2. Create/edit file `~/.ssh/authorized_hosts` so that it contains:
        `no-port-forwarding,no-X11-forwarding,no-agent-forwarding,no-pty,command="<path-to-script>" <X>`
    where X is replaced with the contents of `id_rsa.pub` from step 1
    3. Use `cat /etc/ssh/ssh_host_rsa_key.pub` to get the public key of pip

- On Github
    - Set the secret `SSH_PRIVATE_KEY` to be the contents of the file `id_rsa` generated in step 1
    - Set the secret `SSH_HOST_KEY` to be the output of step 3 above
    - Set `SSH_USER` to my username
    - Set `SSH_HOST` to url of pip
    - Set `DEPLOY_SCRIPT_PATH` to the path to the script to be run by the action

