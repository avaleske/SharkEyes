##SharkEyes

##NVS Development Project

Add setup instructions here at some point...

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

Now that those are and django are running, you can go to `http://localhost:8001/pl_download/testfetch/` to download the netcdf file, and then `http://localhost:8001/pl_plot/testplot/` to plot it. Everything it saved to the synced_dir in your project folder.

Note: The celery console won't give you a prompt back, so you'll have to open a new terminal tab or place it in the background. In Linux, a task may be placed in the background by regaining the command prompt (Ctrl-Z), and typing bg %<task number>. If you watch it, it'll tell you what it's doing with the tasks.

If you change a task, you have to restart celery or it won't see it. This was really confusing for awhile when I had swapped the order of the return arguments.

Also, you can run `sqlite3 db.sqlite3` to get a sql promp and see the database. `.tables` gets you a list of tables, `.headers on` turns on headers for the output when you run a query, and `.mode column` columnates the output so it's actually usable.


###DB Schema
I should probably also explain my thinking regarding the db schema as well.
For netcdf files it's pretty straightforward. At some point I want to add a field for the generated date as well, not just the downloaded date, and we'll have to do a south migration for that and such.

For Overlays, there's Overlays, OverlayDefinitions, and Parameters. An OverlayDefinition knows everything about the type, the name, the function that it needs to call to run it, and whether it's one of the base overlays that are automatically run. (Any overlay someone makes custom won't be a base overlay.)

Parameters will be a way to list the custom parameters that an overlay uses when building it, like temperature range, number of gradient levels, etc. These act like a dictionary, with the OverlayDefinition as the containing object (hence the foreign key.)

An Overlay, then, is an instance of an OverlayDefinition, and knows when it was created and where it's stuff is. Should be easy to get a list of overlay definitions, and then ask for the newest of each corresponding Overlay to display to the user. I imagine this will be done when the view for the menu is built, so the javascript just knows what directory to go to for the tiles...