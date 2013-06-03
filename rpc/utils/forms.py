from django.utils.encoding import force_unicode


class AjaxForm(object):
    """
    Mixin for Django forms to return validation error in dictionary.
    """
    def get_errors(self):
        output = {}
        for key, value in self.errors.items():
            output[key] = '/n'.join([force_unicode(i) for i in value])
        return output
