
class RetentionConfiguration(object):

    @staticmethod
    def get_retention_age_in_months():
        return 36

    @staticmethod
    def get_minimum_number_of_sightings():
        return 2

    @staticmethod
    def get_minimum_number_of_back_links():
        return 1

    @staticmethod
    def set_retention_age(months):
        raise NotImplementedError()

    @staticmethod
    def set_minimum_number_of_sightings(num_sightings):
        raise NotImplementedError()

    @staticmethod
    def set_minimum_number_of_back_links(num_back_links):
        raise NotImplementedError()
