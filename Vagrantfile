VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
    (1..3).each do |i|
        config.vm.define "node-#{i}" do |node|
            node.vm.box = 'ubuntu/trusty64'
            node.vm.provider "virtualbox" do |vb|
                vb.memory = 2048
            end

            node.vm.network :forwarded_port, guest: 5432, host: 5432  # PostgreSQL

            node.vm.provision "server", type: "ansible" do |ansible|
                ansible.playbook = "provision/server.yml"
                ansible.sudo = true
                ansible.extra_vars = {
                    'core_hostname' => "registry-node-#{i}",
                    'postgresql_pg_hba_trust_hosts' => ['all'],
                    'postgresql_listen_addresses' => ['*'],
                }
            end

            node.vm.provision "service", type: "ansible" do |ansible|
                ansible.playbook = "provision/service.yml"
                ansible.sudo = true
            end
        end
    end
end
