from django.test import TestCase

# Create your tests here.
from pl_plot.plotter import Plotter
from pl_plot import plot_functions
FILE_NAME = "ocean_his_3322_04-Feb-2014.nc"


class PlotterTestCase(TestCase):
    def setUp(self):
        None

    def test_plotter_can_plot(self):
        plotter = Plotter(  FILE_NAME)
        data_file = plotter.load_file(FILE_NAME)
        plotter.make_plot(data_file, plot_functions.sst_method())


class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)