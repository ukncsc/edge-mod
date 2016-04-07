
import re
from adapters.certuk_mod.validation import ValidationStatus, FieldValidationInfo
from observable import ObservableValidationInfo

POSITIVE_INTEGER = re.compile(r'^\d+$')
FILE_EXTENSION = re.compile(r'^\.[^\.]+$')
HASHES = {
    r'MD5': (re.compile(r'^[A-Za-z0-9]{32}$'), r'Expected 32 hexadecimal digits'),
    r'MD6': (re.compile(r'^[A-Za-z0-9]{40,128}$'), r'Expected 40-128 hexadecimal digits'),
    r'SHA1': (re.compile(r'^[A-Za-z0-9]{40}$'), r'Expected 40 hexadecimal digits'),
    r'SHA224': (re.compile(r'^[A-Za-z0-9]{56}$'), r'Expected 56 hexadecimal digits'),
    r'SHA256': (re.compile(r'^[A-Za-z0-9]{64}$'), r'Expected 64 hexadecimal digits'),
    r'SHA384': (re.compile(r'^[A-Za-z0-9]{96}$'), r'Expected 96 hexadecimal digits'),
    r'SHA512': (re.compile(r'^[A-Za-z0-9]{128}$'), r'Expected 128 hexadecimal digits'),
    r'SSDeep': (re.compile(r'^(\d+):([\w/+]+):([\w/+]+),"([\w/\s\.-]+)"$'), r'Expected blocksize:hash:hash,"filename"'),
    r'Other': (re.compile(r'^.+$'), r'Expected a hash')
}


class FileValidationInfo(ObservableValidationInfo):

    TYPE = 'FileObjectType'

    def __init__(self, observable_data, **field_validation):
        super(FileValidationInfo, self).__init__(FileValidationInfo.TYPE, observable_data, **field_validation)
        self.size_in_bytes = field_validation.get(r'size_in_bytes')
        self.file_extension = field_validation.get(r'file_extension')
        self.MD5 = field_validation.get(r'MD5')
        self.MD6 = field_validation.get(r'MD6')
        self.SHA1 = field_validation.get(r'SHA1')
        self.SHA224 = field_validation.get(r'SHA224')
        self.SHA256 = field_validation.get(r'SHA256')
        self.SHA384 = field_validation.get(r'SHA384')
        self.SHA512 = field_validation.get(r'SHA512')
        self.SSDeep = field_validation.get(r'SSDeep')
        self.Other = field_validation.get(r'Other')

    @classmethod
    def validate(cls, **observable_data):
        size_in_bytes_validation = cls.__validate_size_in_bytes(observable_data.get(r'size_in_bytes'))
        hashes_validation = cls.__validate_hashes(observable_data.get(r'hashes'))
        file_extension_validation = cls.__validate_file_extension(observable_data.get(r'file_extension'))

        return cls(
            observable_data,
            size_in_bytes=size_in_bytes_validation,
            file_extension=file_extension_validation,
            MD5=hashes_validation.get(r'MD5'),
            MD6=hashes_validation.get(r'MD6'),
            SHA1=hashes_validation.get(r'SHA1'),
            SHA224=hashes_validation.get(r'SHA224'),
            SHA256=hashes_validation.get(r'SHA256'),
            SHA384=hashes_validation.get(r'SHA384'),
            SHA512=hashes_validation.get(r'SHA512'),
            SSDeep=hashes_validation.get(r'SSDeep'),
            Other=hashes_validation.get(r'Other')
        )

    @staticmethod
    def __validate_size_in_bytes(size_in_bytes):
        msg = None
        if size_in_bytes:
            if POSITIVE_INTEGER.match(str(size_in_bytes)):
                pass
            else:
                msg = FieldValidationInfo(ValidationStatus.ERROR, r'Size In Bytes should be a positive integer')
        return msg

    @staticmethod
    def __validate_file_extension(file_extension):
        msg = None
        if file_extension:
            if FILE_EXTENSION.match(str(file_extension)):
                pass
            else:
                msg = FieldValidationInfo(ValidationStatus.WARN, r'File Extension should be .{something}')
        return msg

    @staticmethod
    def __validate_hashes(hashes):
        msgs = {}
        if hashes:
            for hash_ in hashes:
                hash_type = hash_.get(r'type')
                regex, msg = HASHES.get(hash_type.upper())
                if not regex.match(hash_.get(r'simple_hash_value')):
                    msgs[hash_type] = FieldValidationInfo(ValidationStatus.WARN, msg)
        return msgs
