##SharkEyes

NVS Development Project

Add setup instructions here at some point...

Assuming you have your development environment setup, this will help you get up to date with the new changes:
- After you update, make sure you reprovision the vm. (`vagrant reload --provision`)
- Then you need to change to the `/vagrant` directory, and make sure your source is pointing toward the right virtualenv. (`source /home/vagrant/virtualenvs/sharkeyes/bin/activate`)
- Then you need to run syncdb to update the database (`./manage.py syncdb`)
- syncdb will tell you the run migrate on a few other apps, namely, djcelery, pl_plot, and pl_download. For each of these run `./manage.py migrate <app name>`    djcelery might fail, that's ok for some reason.
- Now everything's up to date, and you can start django like normal if you like.

If you want to run tasks, then you need to run rabbitmq and celery:
- To start rabbitmq, run `sudo rabbitmq-server -detatched` Note that it's only one dash.
- To run celery, run `./manage.py celery worker --loglevel=INFO`

Now that those are and django are running, you can go to `http://localhost:8001/pl_download/testfetch/` to download the netcdf file, and then `http://localhost:8001/pl_plot/testplot/` to plot it. Everything it saved to the synced_dir in your project folder.

The celery console won't give you a prompt back, so you'll have to open a new terminal tab. If you watch it, it'll tell you what it's doing with the tasks.

And if you change a task, you have to restart celery or it won't see it. This was really confusing for awhile when I had swapped the order of the return arguments.

Also, you can run `sqlite3 db.sqlite3` to get a sql promp and see the database. `.tables` gets you a list of tables, `.headers on` turns on headers for the output when you run a query, and `.mode column` columnates the output so it's actually usable.