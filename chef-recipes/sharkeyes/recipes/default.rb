directory "/home/vagrant/virtualenvs" do
  owner "vagrant"
  group "vagrant"
  action :create
end

python_virtualenv "/home/vagrant/virtualenvs/sharkeyes" do
  interpreter "python2.7"
  owner "vagrant"
  group "vagrant"
  options "--system-site-packages"
  action :create
    end

yum_repository 'epel' do
  description 'Extra Packages for Enterprise Linux'
  mirrorlist 'http://mirrors.fedoraproject.org/mirrorlist?repo=epel-6&arch=$basearch'
  gpgkey 'http://dl.fedoraproject.org/pub/epel/RPM-GPG-KEY-EPEL-6'
  action :create
end

node['sharkeyes']['packages'].each do |p|
  package p
end

node['sharkeyes']['pip_packages'].each do |pp|
  python_pip pp do
    virtualenv "/home/vagrant/virtualenvs/sharkeyes"
    action :install
  end
end

python_pip "-e git+https://github.com/matplotlib/basemap#egg=basemap" do
    virtualenv "/home/vagrant/virtualenvs/sharkeyes"
    action :install
end

link "/home/vagrant/virtualenvs/sharkeyes/lib/python2.7/site-packages/mpl_toolkits/basemap" do
  to "/home/vagrant/virtualenvs/sharkeyes/src/basemap/lib/mpl_toolkits/basemap/"
end