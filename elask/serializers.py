from marshmallow import (Schema, fields, SchemaOpts, missing, post_dump, pre_dump,
                         pre_load)


class Serializer(Schema):

    EXCEPTIONAL_FIELDS = ['id']

    def __init__(self, *args, **kwargs):
        super(Serializer, self).__init__(*args, **kwargs)
    
    @pre_load
    def load_missing(self, data):
        """
        To make the non specified fields to null
        """
        ret = data.copy()
        for key in self.fields.keys():
            if key not in self.EXCEPTIONAL_FIELDS:
                ret.update({key:ret.get(key, None)})
        return ret

    @pre_dump
    def clean_missing(self, data):
        """
        To make sure the non-saved fields data into None
        """
        ret = data.copy()
        for key in self.fields.keys():
            ret.update({key:ret.get(key, None)})
        return ret
