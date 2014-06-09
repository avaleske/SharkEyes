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

#update repo

yum_repository 'epel' do
  description 'Extra Packages for Enterprise Linux'
  mirrorlist 'http://mirrors.fedoraproject.org/mirrorlist?repo=epel-6&arch=$basearch'
  gpgkey 'http://dl.fedoraproject.org/pub/epel/RPM-GPG-KEY-EPEL-6'
  action :create
end

yum_repository 'elgis' do
    description 'Enterprise Linux GIS'
    baseurl 'http://elgis.argeo.org/repos/6/elgis/x86_64/'
    gpgkey 'http://elgis.argeo.org/RPM-GPG-KEY-ELGIS'
end

#install packages
node['sharkeyes']['packages'].each do |p|
  package p
end

#setup gdal and link to library
source_package 'gdal-1.10.1' do
  download_url "http://download.osgeo.org/gdal/1.10.1/"
  checksum '86b2c71a910d826a7fe6ebb43a532fb7'
  prefix '/usr/local'
end

execute 'link_gdal' do
    command "if grep -Fxq '/usr/local/lib' '/etc/ld.so.conf'; then :; else echo '/usr/local/lib' | tee -a /etc/ld.so.conf; fi"
end

execute 'ldconfig' do
    user 'root'
end

#setup python packages
node['sharkeyes']['pip_packages'].each do |pp|
  python_pip pp do
    virtualenv "/home/vagrant/virtualenvs/sharkeyes"
    timeout 1800
    action :install
  end
end

#and basemap is not in pip.
python_pip "-e git+https://github.com/matplotlib/basemap#egg=Basemap" do
    virtualenv "/home/vagrant/virtualenvs/sharkeyes"
    action :install
end

link "/home/vagrant/virtualenvs/sharkeyes/lib/python2.7/site-packages/mpl_toolkits/basemap" do
  to "/home/vagrant/virtualenvs/sharkeyes/src/basemap/lib/mpl_toolkits/basemap/"
end

link "/usr/lib64/libproj.so" do
    to "/usr/lib64/libproj.so.0"
end