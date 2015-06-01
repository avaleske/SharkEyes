from django.db import models

class FeedbackHistory (models.Model):
    feedback_title = models.CharField(max_length=2000)
    feedback_comments = models.CharField(max_length=2000)

class FeedbackQuestionaire (models.Model):
    ACCURACY_TYPE = (
        ('A', "Accurate"),
        ('NA', "Not Accurate"),
        ('U', "Unsure"),
        ('', ""),
    )
    DEVICE_TYPE = (
        ('C', "Computer"),
        ('SM', "Smartphone"),
        ('T', "Tablet"),
        ('', ""),
    )
    FREQUENCY_TYPES = (
        ('1', "Once"),
        ('2-5', "2 - 5 times"),
        ('6-10', "6 - 10 times"),
        ('10+', "more than 10 times"),
        ('', ""),
    )
    LOCATION_TYPES = (
        ('S', 'At Sea'),
        ('L', 'On Land'),
        ('', ""),
    )

    #Where did you user it?
    usage_location=  models.CharField(max_length=4, choices=LOCATION_TYPES)
    #How many times did you use it?
    usage_frequency = models.CharField(max_length=4, choices=FREQUENCY_TYPES)
    #What did you use?
    usage_device = models.CharField(max_length=4, choices=DEVICE_TYPE)
    #General Comments about the experience?
    usage_comment = models.CharField(max_length=2000)
    #sea surface temperature accuracy?
    ss_temperature_accuracy = models.CharField(max_length=4, choices=ACCURACY_TYPE)
    #surface currents accuracy
    ss_currents_accuracy = models.CharField(max_length=4, choices=ACCURACY_TYPE)
    #wave plot accuracy
    wave_accuracy = models.CharField(max_length=4, choices=ACCURACY_TYPE)
    #wind plot accuracy
    wind_accuracy = models.CharField(max_length=4, choices=ACCURACY_TYPE)
    #How does seacast.org compare with other forecasting system?
    usage_comparison = models.CharField(max_length=2000)
    #What are three things you like about seacst.org
    usage_likes = models.CharField(max_length=2000)
    #What are the first three things you would change?
    usage_suggestion = models.CharField(max_length=2000)
    #What other ocean condition would you like to see?
    usage_model_suggestion = models.CharField(max_length=2000)
