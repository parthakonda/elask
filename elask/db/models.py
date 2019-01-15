from elasticsearch_dsl import (Boolean, Date, DocType, Integer, Keyword,
                               Nested, String, Text)


class Model(DocType):
    """
    Adding custom behaviour for DocType
    """
    pass


class DateField(Date):
    """
    Adding custom behaviour for Date
    """
    pass


class IntegerField(Integer):
    """
    Adding custom behaviour for Integer
    """
    pass


class KeywordField(Keyword):
    """
    Adding custom behaviour for Keyword Field
    """
    pass


class NestedField(Nested):
    """
    Adding custom behaviour for nested
    """
    pass


class AnalyzerField(String):
    """
    Adding custom behaviour for String
    """
    pass


class CharField(String):
    """
    Adding custom bahaviour for String
    """
    def __init__(self, *args, **kwargs):
        kwargs.update({
            'index':'not_analyzed'
        })
        super(CharField, self).__init__(*args, **kwargs)


class TextField(Text):
    """
    Adding custom behaviour for Text
    """
    pass


class BooleanField(Boolean):
    """
    Adding custom behaviour for Boolean
    """
    pass