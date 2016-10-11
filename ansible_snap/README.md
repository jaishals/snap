#Ansible Snap

This will Setup localhost with elasticsearch, kibana and nginx
	elasticsearch : v 2.x
    kibana        : v 4.6.1

The Ansible playbook is tested with ubuntu systems.

UserGuide:
----------
1. Install Ansible http://docs.ansible.com/intro_installation.html
2. Add below lines to /etc/ansible/hosts
	[localhost]
		localhost ansible_connection=local
3. To Run Ansible playbook in order to setup ES and Kibana
      sudo ansible-playbook snap_es.yml
