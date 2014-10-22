##SharkEyes - NVS Development Project

###Setup

####Installing prereqs:
All these requirements should be cross platform. If you're on Windows, I like using the Git Bash for these over Command Prompt, but that's just me. Also, throughout these steps I mention the project directory, which is the directory that you clone from GitHub that contains `manage.py` and the hidden `.git` directory.
- Install [Vagrant](www.vagrantup.com), [Git](http://git-scm.com/), and [VirtualBox](https://www.virtualbox.org/wiki/Downloads)
- Install [PyCharm](http://www.jetbrains.com/pycharm/) (There's a free 30 day trial and free academic license.)
- Install [Python](https://www.python.org/) or use the Python that comes with your system. The system python, however, is likely out of date.    
- Install Python Pip using instructions from [here](https://pip.pypa.io/en/latest/installing.html). (Using the `get-pip.py` script described in the links makes this pretty easy.)
- This step is ikely Windows only. You have some dependencies you need to install before install fabric:
  - Install the pycrypto binaries with `easy_install http://www.voidspace.org.uk/downloads/pycrypto26/pycrypto-2.6.win32-py2.7.ex`
  - Then `pip install paramiko`
- Install [Fabric](http://www.fabfile.org/installing.html) with `pip install fabric`. You can do this in a virtualenv if you want, but it shouldn't conflict with anything so that's likely not critical.
- Clone this repo to local drive using the button (if you use Git Desktop) or the url on the side. If you want to use ssh so you don't have to keep entering passwords, learn how to setup ssh keys with GitHub  [here](https://help.github.com/articles/generating-ssh-keys/)
  - When cloning, keep in mind that you'll be adding a few directories at the same level as the project directory, so cloning the recommended approach is to make a directory for the project, cd into that, and then clone the repo. (So for example, create directory at `~/code/sharkyes/` and run `git clone` from inside that directory.)
  - Clone the repo with `git clone git@github.com:avaleske/SharkEyes.git` for ssh,
  - or `git clone https://github.com/avaleske/SharkEyes.git` for http.
- Finally, create a `media/` directory at the same level as your project directory. For the example directory structure listed above, it'd be at `~/code/sharkeyes/media/`, since the repo you just cloned is at `~/code/sharkeyes/SharkEyesCore/`.
#####Bringing the virtual machine online:
- While at this point you can just run `vagrant up`  to download and configure the centos box, it's recommended to first download the base box manually.
  - To download box base manually, you can do `vagrant box add centos65 https://github.com/2creatives/vagrant-centos/releases/download/v6.5.3/centos65-x86_64-20140116.box`
  - Then do `vagrant up` to bring the box online. You'll need to be in or below the directory where the vagrantfile is located. With our running example, you'd need to be in `~/code/sharkeyes/SharkEyesCore/`.
  - You should now be able to run `vagrant ssh` from inside the project directory and automatically ssh into the virtual machine. To suspend or shutdown the vm, use `vagrant suspend` or `vagrant halt`, respectively. To bring your VM online, it's always `vagrant up`.
  - Also check that your local project folder has been mounted in the VM at `/vagrant/`. This makes it easy to edit code in PyCharm or Sublime or something locally, and then run it in the VM without having to copy it.
  - (Windows users, this would be a good place to check that trying to resume after a `vagrant suspend` doesn't wipe your VM. There's a bug in some versions of VirtualBox that causes it to lose track of suspended VMs, and then you have to start from scratch. If this is the case, always use `vagrant halt`.)

####To configure the VM:
Ok, so you've got the vagrant vm up and running. Great! We use fabric to provision the VM and set it up with everything we need. This will take awhile to download and compile everything we need, so you can leave it for a bit, but unfortunately it'll need some babysitting at the end.
#####Setup passwords:
We store the passwords in a separate file that we keep out of source control. Make some up now. You'll need them later in setup, but you can always reference the file you're about to create.
- In `<project dir>/SharkEyesCore` there's a file called `settings_local.template`. Make a copy of this named `settings_local.py`
- In this `settings_local.py`, make up values for the BROKER_PASSWORD and the PASSWORD item under DATABASES. Also, choose a secret key, which should be an ASCII string that's about 40 characters long.
- Finally, set the DEBUG and TEMPLATE_DEBUG flags to true if you want the runserver and static files to work.
#####Setup everything else:
Ok, awesome, vagrant works and you have passwords setup. Now to run the setup script. We use fabric to do this.
- From the same directory as `fabfile.py`, or below it, run `fab vagrant uname`. This will connect to the VM, and run `uname -a` remotely for you. If this worked, then go to the next step.
- Now we install everything on the VM. To do this, run `fab vagrant provision`. This will take a long time, (possibly hours). It should do most things on it's own, but will need babysitting at the end. Just do what it asks you to do. If something fails you should be able to run `fab vagrant provision` again, as it should be indempotent. If you need to, you can run any function in `fabfile.py` with `fab vagrant <function name>`.
- Once that finishes, do `fab vagrant deploy` to run the Django setup scripts and run the database migrations.
- Then do `fab vagrant startdev` and do what it says to bring all the background services online. You'll need to run this anytime you cold boot the VM. (If you're just resuming, it should be fine.)
- At this point, you can move on and configure PyCharm, or `vagrant ssh` into the machine and start the runserver manually.
  - To start the runserver manually, source the virtualenv by doing `source /opt/sharkeyes/env_sharkeyes/bin/activate`
  - Then, from the project directory, do `./manage.py runserver 0.0.0.0:8000`

####To configure PyCharm:
- From PyCharm go File->Open and choose the project directory. It should recognize stuff, give it a chance to do that.
- Then you need to setup the project interpreter to use the interpreter in your virtual machine. Make sure the VM is up before doing this:
  - Go to PyCharm Preferences -> Project Interpretor
  - Click the gear to the right of the Project Interpeter bar, and then remote, and then the 'vagrant' radio button. If it asks, your vagrant instance folder is the project folder.
  - In the Python Interpreter Path put `/home/vagrant/virtualenvs/sharkeyes/bin/python`
  - <img src="resources/configure_interpreter.png?raw=true">
  - Then click ok. It'll connect to the vagrant instance and learn what's installed there, which might take a minute or two.
- Then go to PyCharm Preferences -> Django.
  - Check the box to enable Django.
  - The project root is your project folder. Point 'Settings' at `settings.py`, and point 'Manage script' at `manage.py`. These are both relative to the project root.
  - <img src="resources/pycharm_django.png?raw=true">
- Then setup the site configuration to run the project from within PyCharm:
  - At the top of the PyCharm window there’s a play button and a down arrow to the left of it. Choose that, and then 'edit configurations'.
  - Set the host to `0.0.0.0`, and the Port to `8000`.
  - Check 'no-reload' so that it doesn’t automatically reload when you change code. Or don't if you want it to do that.
  - Make sure that the python interpreter is the remote one you made earlier.
  - Set two environment variables by clicking on the `...` to the right of the field.
    - set `DJANGO_SETTINGS_MODULE` equal to `SharkEyesCore.settings`
    - and set `PYTHONUNBUFFERED` equal to 1.
  - And add a path mapping where the local path is your project folder, and the remote path is `/opt/sharkeyes/src`.
- This should be everything. You should be able to hit run, and get then go to `localhost:8001` in your browser and project home page. If you want to debug, set a breakpoint and hit the bug to the right of the play button.

####Test things:
For any of these urls, you can go to the terminal window where celery is running to watch the tasks go by, even after the pageload times out. Everything is saved to the `media/` directory that's at the same level as your project directory. All of the functions that these urls call can also be called from the django console. Careful to ensure you're calling them as celery tasks (Do it the ways it's done in the corresponding `views.py` file) rather than a normal function, or else you'll lose any concurrency benefits and won't be able to monitor progress with celery.
- Now that Django is running, you can go to `http://localhost:8001/pl_download/testfetch/` to download the netcdf files for the next few days.
- If you have a lot of time, then `http://localhost:8001/pl_plot/testplot/` to plot the files for the next few days. If you don't have a lot of time, do the next bullet.
- You can also use the django console in PyCharm to run functions that only plot one plot, instead of all of them. To plot something from the django console you'd need to do `from pl_plot.models import OverlayManager`, then `OverlayManager.make_plot.delay(1)`. This would plot the sst overlay for the first time index of the most recent netcdf file. Note that due to assumptions in the javascript, this one plot may not show up in the picker until you've plotted all the plots for that day.
- To tile these plots, go to `https://localhost:8001/pl_chop/testchop/`. These will take a long time if you have many overlays. It will go faster if you give your VM multiple cores.

###Notes
The celery console won't give you a prompt back, so you'll have to open a new terminal tab or place it in the background. In Linux, a task may be placed in the background by regaining the command prompt (Ctrl-Z), and typing bg %<task number>. If you watch it, it'll tell you what it's doing with the tasks.

If you change a task, you have to restart celery or it won't see it. This was really confusing for awhile when I had swapped the order of the return arguments.

If you're using sqlite (and if you followed the above instuctions you're not - it should be an option again soon) you can run `sqlite3 db.sqlite3` to get a sql promp and see the database. `.tables` gets you a list of tables, `.headers on` turns on headers for the output when you run a query, and `.mode column` columnates the output so it's actually usable.

Sometimes you'll try to start the runserver and the port will be in use. There's likely a runserver instance running that got lost. In the VM, do `sudo ps aux | grep -i manage` and kill the runserver process. Just restarting the VM can fix this too.

If you try to run a fabric command and get an ssh key error, and also recently destroyed your vm and are trying to build a new one, it's likely because fabric is expecting the old ssh key. Run `ssh-keygen -R [127.0.0.1]:2222` to fix it. Type it exactly. Unlike convention the brackets don't mean to replace their contents.)

###Git Organization
We have structured the project Git repository so that any major feature development is done in a specific `feature` branch, and the `feature` branches are merged into the `develop` branch when they're complete. Then, when a set of features is ready for release and `develop` is in a stable state, `develop` is merged into `master`, and `master` is what is checked out in production. This ensures that `master` is always the same as what is running in production. If a hot-fix is necessary, a branch for the hot-fix is created from `master`, and then, when it is completed, it is merged into both `master` and `develop`.

###DB Schema
I should probably also explain my thinking regarding the db schema as well.
For netcdf files it's pretty straightforward. Information about when they were downloaded and such is in the DataFile model.

For Overlays, there's Overlays, OverlayDefinitions, and Parameters. An OverlayDefinition knows everything about the type, the name, the function that it needs to call to run it, and whether it's one of the base overlays that are automatically run. (Any overlay someone makes custom won't be a base overlay.)

Parameters will be a way to list the custom parameters that an overlay uses when building it, like temperature range, number of gradient levels, etc. These act like a dictionary, with the OverlayDefinition as the containing object (hence the foreign key.)

An Overlay, then, is an instance of an OverlayDefinition, and knows when it was created, where it's stuff is, and what datetime it applies at.
