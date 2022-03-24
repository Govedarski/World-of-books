from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible


@deconstructible
class MaxSizeInMBValidator:
    def __init__(self, max_size_in_mb):
        self.max_size_in_mb = max_size_in_mb

    def __call__(self, file):
        if file.file.size > self.__max_size_in_bytes():
            raise ValidationError(self.__error_message())

    def __max_size_in_bytes(self):
        return self.max_size_in_mb * 1024 * 1024

    def __error_message(self):
        return f'File is bigger than max size ({self.max_size_in_mb} MB)'


@deconstructible
class OnlyLetterValidator:
    ERROR_MESSAGE = 'The field should consist of letters only!'

    def __call__(self, value):
        if not value.isalpha():
            raise ValidationError(self.ERROR_MESSAGE)

@deconstructible
class OnlyNumberValidator:
    ERROR_MESSAGE = 'The field should consist of numbers only!'

    def __call__(self, value):
        if not value.isnumeric():
            raise ValidationError(self.ERROR_MESSAGE)