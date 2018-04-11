class TimeSliceHelper:
    """
    It is an utility class to help filtering. It is used by the managers
    like e.g. in app "Cart" the "VenteManager".
    """

    def __init__(self, model):
        self.model = model
        self.qs = self.model.objects.all()

    def _set_year_qs(self, year):
        if self.model._meta.model_name == 'vente':
            self.qs = self.qs.filter(date__year=year)
        elif self.model._meta.model_name == 'costs':
            self.qs = self.qs.filter(creation_date__year=year)
        elif self.model._meta.model_name == 'article':
            self.qs = self.qs.filter(date_added__year=year)
        else:
            raise Exception("Model {0} not handled.".format(self.model._meta.model_name))


    def _set_start_end_date_qs(self, start_date, end_date):
        if self.model._meta.model_name == 'vente':
            self.qs = self.qs.filter(date__range= (start_date, end_date))
        elif self.model._meta.model_name == 'costs':
            self.qs = self.qs.filter(creation_date__range=(start_date, end_date))
        elif self.model._meta.model_name == 'article':
            self.qs = self.qs.filter(date_added__range=(start_date, end_date))
        else:
            raise Exception("Model {0} not handled.".format(self.model._meta.model_name))


    def _set_start_date_qs(self, start_date):
        if self.model._meta.model_name == 'vente':
            self.qs = self.qs.filter(date__gte=start_date)
        elif self.model._meta.model_name == 'costs':
            self.qs = self.qs.filter(creation_date__gte=start_date)
        elif self.model._meta.model_name == 'article':
            self.qs = self.qs.filter(date_added__gte=start_date)
        else:
            raise Exception("Model {0} not handled.".format(self.model._meta.model_name))


    def _set_end_date_qs(self, end_date):
        if self.model._meta.model_name == 'vente':
            self.qs = self.qs.filter(date__lte=end_date)
        elif self.model._meta.model_name == 'costs':
            self.qs = self.qs.filter(creation_date__lte=end_date)
        elif self.model._meta.model_name == 'article':
            self.qs = self.qs.filter(date_added__lte=end_date)
        else:
            raise Exception("Model {0} not handled.".format(self.model._meta.model_name))


    def get_objects(self,  year=None, branch=None, start_date=None, end_date=None):
        objects = []
        if year:
            self._set_year_qs(year)
        if start_date and end_date:
            self._set_start_end_date_qs(start_date, end_date)

        if start_date and not end_date:
            self._set_start_date_qs(start_date)

        if not start_date and end_date:
            self._set_end_date_qs(end_date)


        if branch != None:
            objects = self.qs.filter(branch=branch)
        else:
            objects = self.qs.all()
        return objects


