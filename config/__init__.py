"""PfunzoBridge Django Configuration Package."""
import copy
from django.template.context import BaseContext

# Python 3.14 compatibility patch for Django BaseContext.__copy__
_original_base_copy = getattr(BaseContext, '__copy__', None)

def _py314_basecontext_copy(self):
    cls = self.__class__
    dup = cls.__new__(cls)
    dup.dicts = self.dicts[:]
    return dup

BaseContext.__copy__ = _py314_basecontext_copy
