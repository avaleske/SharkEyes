from django.test.simple import DjangoTestSuiteRunner
from django.core.management import call_command
from django.core.cache import cache



class CustomTestRunner(DjangoTestSuiteRunner):
  """ A test runner to test without database creation """

  def setup_databases(self, **kwargs):
    """ Override the database creation defined in parent class """
    print "Creating Test Database"
    pass

  def teardown_databases(self, old_config, **kwargs):
    """ Override the database teardown defined in parent class """
    print "Deleting Test Database"
    pass