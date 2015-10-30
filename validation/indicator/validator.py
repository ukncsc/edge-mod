
from .indicator import IndicatorValidationInfo


class IndicatorValidator(object):

    @staticmethod
    def validate(**indicator_data):
        # Perhaps here we could apply some field mapping to always pass the correct data to
        # IndicatorValidationInfo.validate
        return IndicatorValidationInfo.validate(**indicator_data)
