VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

    config.vm.define :service do |workstation|
        workstation.vm.box = 'ubuntu/trusty64'

        workstation.vm.provider "virtualbox" do |vb|
            vb.memory = 2048
        end

        workstation.vm.network :forwarded_port, guest: 5432, host: 5432  # PostgreSQL

        workstation.vm.provision "server", type: "ansible" do |ansible|
            ansible.playbook = "provision/server.yml"
            ansible.sudo = true
            ansible.extra_vars = {
                'core_hostname' => 'registry',
                'postgresql_pg_hba_trust_hosts' => ['all'],
                'postgresql_listen_addresses' => ['*'],
            }
        end

        workstation.vm.provision "service", type: "ansible" do |ansible|
            ansible.playbook = "provision/service.yml"
            ansible.sudo = true
        end
    end
end
