__author__ = 'avaleske'
from django.test import TestCase
from se_pipeline.plotter import Plotter

FILE_NAME = "ocean_his_3322_04-Feb-2014.nc"


class PlotterTestCase(TestCase):
    def setUp(self):
        None

    def test_plotter_can_plot(self):
        plotter = Plotter()
        data_file = plotter.load_file(FILE_NAME)
        plot = plotter.make_temp_plot(data_file)