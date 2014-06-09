##SharkEyes
##NVS Development Project

This was last updated on 6/9/2014. There is likely a more up to date version. Email avaleske@gmail.com with Sharkeyes in the subject line to get access to the newest version of the repo.

###Setup

To setup the vm
- install pycharm, vagrant, git, virtualbox
- clone repo to local drive
- `git submodule init`
- `git submodule update`
- run `vagrant up` to download and configure the centos box.
- to download box base beforehand, you can also do `vagrant box add CentOS6_4_Dev http://developer.nrel.gov/downloads/vagrant-boxes/CentOS-6.4-x86_64-v20130731.box` and then do vagrant up

To configure PyCharm
- First, open the project folder in pycharm. It should recognize stuff, let it do it.
- Then you need to setup the project interpreter to use the interpreter in your virtual machine.
- So do pycharm settings > project interpretor > configure interpretors
- Click add, and then remote, and then “fill from vagrant config” This might glitch and take awhile, but should work after a few tries. If it asks, your vagrant instance folder is the project folder.
- In the Python Interpreter Path put `/home/vagrant/virtualenvs/sharkeyes/bin/python`
- Then go to pycharm settings > django support. Settings is for `settings.py`, and the manage script is for `manage.py`. These are both relative to the project root.
- Then, at the top, of the pycharm window, there’s a play button and a down arrow to the left of it. Choose that, and then edit configurations.
- Set the host to `0.0.0.0`, and the Port to `8000`.
- Check no-reload so that it doesn’t automatically reload when you change code. Or don't if you want it to do that.
- Make sure that the python interpreter is the remote one you chose earlier.
- This should be everything. You should be able to hit run, and get then go to `localhost:8001` and project home page.



Assuming you have your development environment setup, this will help you get up to date with the new changes:
- After you update, make sure you reprovision the vm. (`vagrant reload --provision`)

###Initializing Server
To start the Django server, simply change to the `/vagrant` directory and run (`sh init.sh`). This will perfom the following actions:
- Ensure your source is pointing toward the right virtualenv. (`source /home/vagrant/virtualenvs/sharkeyes/bin/activate`)
- Run syncdb to update the database (`./manage.py syncdb`)
- syncdb will tell you the run migrate on a few other apps, namely, djcelery, pl_plot, and pl_download. For each of these run `./manage.py migrate <app name>`    djcelery might fail, that's ok for some reason.
- To start rabbitmq, run `sudo rabbitmq-server -detatched` Note that it's only one dash.
- To run celery, run `./manage.py celery worker --loglevel=INFO`
- Start the Django server.

Now that those are and django are running, you can go to `http://localhost:8001/pl_download/testfetch/` to download the netcdf files for the next few days, and then `http://localhost:8001/pl_plot/testplot/` to plot the files for the next few days. Everything it saved to the synced_dir in your project folder. You can also use the django console in PyCharm to run function that only plot one plot, instead of all of them.

Note: The celery console won't give you a prompt back, so you'll have to open a new terminal tab or place it in the background. In Linux, a task may be placed in the background by regaining the command prompt (Ctrl-Z), and typing bg %<task number>. If you watch it, it'll tell you what it's doing with the tasks.

If you change a task, you have to restart celery or it won't see it. This was really confusing for awhile when I had swapped the order of the return arguments.

Also, you can run `sqlite3 db.sqlite3` to get a sql promp and see the database. `.tables` gets you a list of tables, `.headers on` turns on headers for the output when you run a query, and `.mode column` columnates the output so it's actually usable.

###Git Organization
We have structured the project Git repository so that any major feature development is done in a specific `feature` branch, and the `feature` branches are merged into the `develop` branch when they're complete. Then, when a set of features is ready for release and `develop` is in a stable state, `develop` is merged into `master`, and `master` is what is checked out in production. This ensures that `master` is always the same as what is running in production. If a hot-fix is necessary, a branch for the hot-fix is created from `master`, and then, when it is completed, it is merged into both `master` and `develop`.

###DB Schema
I should probably also explain my thinking regarding the db schema as well.
For netcdf files it's pretty straightforward. At some point I want to add a field for the generated date as well, not just the downloaded date, and we'll have to do a south migration for that and such.

For Overlays, there's Overlays, OverlayDefinitions, and Parameters. An OverlayDefinition knows everything about the type, the name, the function that it needs to call to run it, and whether it's one of the base overlays that are automatically run. (Any overlay someone makes custom won't be a base overlay.)

Parameters will be a way to list the custom parameters that an overlay uses when building it, like temperature range, number of gradient levels, etc. These act like a dictionary, with the OverlayDefinition as the containing object (hence the foreign key.)

An Overlay, then, is an instance of an OverlayDefinition, and knows when it was created and where it's stuff is. Should be easy to get a list of overlay definitions, and then ask for the newest of each corresponding Overlay to display to the user. I imagine this will be done when the view for the menu is built, so the javascript just knows what directory to go to for the tiles...
